import sqlalchemy
import sqlalchemy as sqla

from dateutil import parser
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Role
from flask_script import Manager, Option
from sqlalchemy.orm.attributes import InstrumentedAttribute

from superset import app, utils, db
from superset_config import RAPIDPRO_API_KEY, SQLALCHEMY_DATABASE_URI, \
    SQLALCHEMY_ROOT_DATABASE_URI

from temba_client.v2 import TembaClient
from chpro.db import rapidpro

config = app.config
celery_app = utils.get_celery_app(config)

from flask_script import Command


def process_column(table, data, name):
    if not data[name]:
        return

    if (isinstance(table.columns[name].type, sqla.types.DateTime) or
        isinstance(table.columns[name].type, sqla.types.Date)):
        return parser.parse(data[name])

    return data[name]


class ImportRapidProData(Command):
    """Imports runs from the RapidPro API"""

    order_field = 'modified_on'

    def get_options(self):
        return [
            Option('-a', '--after', dest='after', default=None),
            Option('-b', '--before', dest='before', default=None),
        ]

    def run(self, after, before):
        client = TembaClient('rapidpro.io', RAPIDPRO_API_KEY)
        engine = sqla.create_engine(SQLALCHEMY_DATABASE_URI)

        if not engine.dialect.has_table(engine, rapidpro.run.name):
            rapidpro.run.create(engine)

        conn = engine.connect()

        q = sqla.select([rapidpro.run]).order_by(
            sqla.desc(rapidpro.run.c[self.order_field]))
        latest_run = conn.execute(q).first()

        extras = {}
        if after:
            extras['after'] = parser.parse(after)
        elif latest_run:
            extras['after'] = latest_run[self.order_field]

        if before:
            extras['before'] = parser.parse(before)

        print(
            f"Fetching runs between {extras.get('after')} and {extras.get('before')}")

        batches = client.get_runs(flow='7a376c32-fc78-49c9-b200-2f462efb7b10',
                                  **extras) \
            .iterfetches(retry_on_rate_exceed=True)

        cols = [i.key for i in rapidpro.run.columns]

        for batch in batches:
            print('Importing a batch of runs...')
            for run in batch:
                data = run.serialize()
                print(f'Importing Run {data["id"]}')
                insert = rapidpro.run.insert().values(
                    **{c: process_column(rapidpro.run, data, c) for c in cols})
                try:
                    conn.execute(insert)
                except Exception as e:
                    print(f'Error during: {e.orig}')


EDITOR_SQL = '''
-- adds SQL Lab permissions
replace into ab_permission_view_role (permission_view_id, role_id)
  select apv.id, ar.id from ab_permission_view as apv
  inner join ab_role as ar on ar.name = "Editor"
  where apv.id in (select permission_view_id from ab_permission_view_role where role_id = (select id from ab_role where name = "sql_lab"));

-- adds Manage Viewers permissions
replace into ab_permission_view_role (permission_view_id, role_id)
  select apv.id, ar.id from ab_permission_view as apv
  inner join ab_role as ar on ar.name = "Editor"
    where permission_id in (select id from ab_permission where name in ('can_add', 'can_download', 'can_edit', 'can_list', 'can_show', 'can_delete', 'muldelete', 'mulexport'))
      and
    view_menu_id = (select id from ab_view_menu where name = "Manage Viewers");
'''

VIEWER_SQL = '''
-- remove can delete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_delete")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can add
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_add")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can add slices
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_add_slices")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can copy dash
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_copy_dash")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can delete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_delete")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can edit
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_edit")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can import dashboards
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_import_dashboards")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can override role permissions
-- role will not any by default

-- remove muldelete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "muldelete")) and role_id = (select id from ab_role where name = "Viewer");

-- add data access
insert ignore into ab_permission_view_role (permission_view_id, role_id)
  select apv.id, ar.id from ab_permission_view as apv
  inner join ab_role as ar on ar.name = "Viewer"
    where permission_id = (select id from ab_permission where name = 'all_datasource_access')
      and
    view_menu_id = (select id from ab_view_menu where name = 'all_datasource_access');
'''


class SetupPermissions(Command):
    """Programatically setup the chpro permissions"""

    def run(self):
        session = db.session()

        # Editor
        alpha = session.query(Role).filter(Role.name == 'Alpha').first()
        editor = session.query(Role).filter(Role.name == 'Editor').first()
        if not editor:
            editor = Role()
        editor.name = 'Editor'
        editor.permissions = alpha.permissions
        print('\nCopying Alpha role to Editor...')
        SQLAInterface(Role, session).add(editor)
        print('Generating custom Editor permissions from SQL...')
        db.engine.execute(EDITOR_SQL)
        print('Editor role created successfully.\n')

        # Viewer
        gamma = session.query(Role).filter(Role.name == 'Gamma').first()
        viewer = session.query(Role).filter(Role.name == 'Viewer').first()
        if not viewer:
            viewer = Role()
        viewer.name = 'Viewer'
        viewer.permissions = gamma.permissions
        print('Copying Gamma role to Viewer...')
        SQLAInterface(Role, session).add(viewer)
        print('Generating custom Viewer permissions from SQL...')
        db.engine.execute(VIEWER_SQL)
        print('Viewer role created successfully.')

        engine = sqlalchemy.create_engine(SQLALCHEMY_ROOT_DATABASE_URI)
        root_conn = engine.raw_connection()
        with root_conn.cursor() as cursor:
            print('\nGranting all privileges to the superset db user...')
            grant = '''
            GRANT ALL PRIVILEGES ON *.* TO 'superset'@'%';
            FLUSH PRIVILEGES;
            '''
            cursor.execute(grant)


class CustomPostInstallFixes(Command):
    """Post install fixes"""

    def run(self):
        print('Fixing column type length...')
        db.engine.execute('ALTER TABLE table_columns MODIFY type varchar(255);')
        print('done')


manager = Manager(app)
manager.add_command('import_rapidpro_data', ImportRapidProData())
manager.add_command('custom_post_install_fixes', CustomPostInstallFixes())
manager.add_command('setup_permissions', SetupPermissions())
