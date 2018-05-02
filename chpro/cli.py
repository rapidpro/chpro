import sqlalchemy

from dateutil import parser
from flask_script import Manager, Option
from sqlalchemy import desc

from superset import app, utils
from superset_config import RAPIDPRO_API_KEY, SQLALCHEMY_DATABASE_URI

from temba_client.v2 import TembaClient
from chpro.db import rapidpro

config = app.config
celery_app = utils.get_celery_app(config)


from flask_script import Command


def process_column(table, data, name):
    if not data[name]:
        return

    if (isinstance(table.columns[name].type, sqlalchemy.types.DateTime) or
        isinstance(table.columns[name].type, sqlalchemy.types.Date)):
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
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
        conn = engine.connect()

        q = sqlalchemy.select([rapidpro.run]).order_by(desc(rapidpro.run.c[self.order_field]))
        latest_run = conn.execute(q).first()

        extras = {}
        if after:
            extras['after'] = parser.parse(after)
        elif latest_run:
            extras['after'] = latest_run[self.order_field]

        if before:
            extras['before'] = parser.parse(before)

        print(f"Fetching runs between {extras.get('after')} and {extras.get('before')}")

        batches = client.get_runs(flow='7a376c32-fc78-49c9-b200-2f462efb7b10', **extras)\
            .iterfetches(retry_on_rate_exceed=True)

        cols = [i.key for i in rapidpro.run.columns]

        for batch in batches:
            print('Importing a batch of runs...')
            for run in batch:
                data = run.serialize()
                print(f'Importing Run {data["id"]}')
                insert = rapidpro.run.insert().values(**{c: process_column(rapidpro.run, data, c) for c in cols})
                try:
                    conn.execute(insert)
                except Exception as e:
                    print(f'Error during: {e.orig}')


class LoadInitialData(Command):
    """Load initial chpro data"""

    def create_rapidpro_table(self):
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
        rapidpro.run.create(engine)

    def run(self):
        self.create_rapidpro_table()

manager = Manager(app)
manager.add_command('import_rapidpro_data', ImportRapidProData())
manager.add_command('load_initial_data', LoadInitialData())

