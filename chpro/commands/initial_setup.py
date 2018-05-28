import sqlalchemy

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import Role
from flask_script import Manager

from superset import app, utils, db
from superset_config import SQLALCHEMY_ROOT_DATABASE_URI

from flask_script import Command


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

