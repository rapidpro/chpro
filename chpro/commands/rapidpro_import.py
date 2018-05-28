import sqlalchemy as sqla

from dateutil import parser

from flask_script import Option, Command

from temba_client.v2 import TembaClient
from superset_config import RAPIDPRO_API_KEY, SQLALCHEMY_DATABASE_URI

from chpro.db import rapidpro


def process_column(table, data, name):
    if '__' in name:
        first, second, *rest = name.split('__')
        # Potentially we could go deeper in the indirection
        try:
            return data[first][second]
        except KeyError:
            print(f'Warning: Indirect key missing: {name}')
            return

    try:
        if data[name] is None:
            print(f'Warning: Key missing: {name}')
            return
    except KeyError:
        print(f'Warning: Key missing: {name}')
        return

    if (isinstance(table.columns[name].type, sqla.types.DateTime) or
        isinstance(table.columns[name].type, sqla.types.Date)):
        return parser.parse(data[name])

    return data[name]


class ImportRapidProRun(Command):
    """Imports runs from the RapidPro API"""

    order_field = 'modified_on'

    def get_options(self):
        return [
            Option('flow'),
            Option('-a', '--after', dest='after', default=None),
            Option('-b', '--before', dest='before', default=None),
        ]

    def run(self, flow, after, before):
        client = TembaClient('rapidpro.io', RAPIDPRO_API_KEY)
        engine = sqla.create_engine(SQLALCHEMY_DATABASE_URI,
                                    encoding='utf8')

        if not engine.dialect.has_table(engine, rapidpro.run.name):
            rapidpro.run.create(engine)

        conn = engine.connect()

        q = sqla.select([rapidpro.run])\
            .where(rapidpro.run.c.flow__uuid==flow)\
            .order_by(sqla.desc(rapidpro.run.c[self.order_field]))
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

        batches = client.get_runs(flow=flow, **extras) \
            .iterfetches(retry_on_rate_exceed=True)

        cols = [i.key for i in rapidpro.run.columns]

        for batch in batches:
            print(f'Importing a batch of runs ({len(batch)})...')
            for run in batch:
                if latest_run and run.id == latest_run.id:
                    print(f'Skipping already imported Run {run.id}.')
                    continue
                data = run.serialize()
                print(f'Importing Run {data["id"]}')
                insert = rapidpro.run.insert().values(
                    **{c: process_column(rapidpro.run, data, c) for c in cols})
                try:
                    conn.execute(insert)
                except Exception as e:
                    print(f'Error during: {e.orig}')
