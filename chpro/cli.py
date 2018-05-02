import datetime

import sqlalchemy
from dateutil import parser
from flask_script import Manager
from superset import app, utils
from temba_client.v2 import TembaClient
from superset_config import RAPIDPRO_API_KEY, SQLALCHEMY_DATABASE_URI

from chpro.db import rapidpro

config = app.config
celery_app = utils.get_celery_app(config)


from flask_script import Command

class ImportRapidProData(Command):
    """Imports runs from the RapidPro API"""

    def run(self):
        client = TembaClient('rapidpro.io', RAPIDPRO_API_KEY)
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
        conn = engine.connect()

        batches = client.get_runs(flow='7a376c32-fc78-49c9-b200-2f462efb7b10',
                                  after=datetime.datetime(2018, 5, 2)).iterfetches(retry_on_rate_exceed=True)

        cols = [i.key for i in rapidpro.run.columns]

        def process_column(table, data, name):
            if not data[name]:
                return

            if isinstance(table.columns[name].type, sqlalchemy.types.Date):
                return parser.parse(data[name])

            return data[name]

        for batch in batches:
            for run in batch:
                data = run.serialize()
                insert = rapidpro.run.insert().values(**{c: process_column(rapidpro.run, data, c) for c in cols})
                print(f'Inserting: {data}')
                conn.execute(insert)


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

