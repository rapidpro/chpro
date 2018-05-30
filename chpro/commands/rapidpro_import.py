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


class RapidProImport():
    """Base class for rapid pro import commands"""

    order_field = 'modified_on'
    table = None
    id_field = 'uuid'

    def get_options(self):
        return [
            Option('-a', '--after', dest='after', default=None),
            Option('-b', '--before', dest='before', default=None),
        ]

    def latest(self, conn):
        q = sqla.select([self.table])\
            .order_by(sqla.desc(self.table.c[self.order_field]))
        return conn.execute(q).first()

    def api_call(self):
        raise NotImplementedError()

    def process(self, after, before):
        client = TembaClient('rapidpro.io', RAPIDPRO_API_KEY)
        engine = sqla.create_engine(SQLALCHEMY_DATABASE_URI,
                                    encoding='utf8')

        if self.table is None:
            raise ValueError('Improperly configured. '
                             'A table needs to be provided')

        if not engine.dialect.has_table(engine, self.table.name):
            self.table.create(engine)

        conn = engine.connect()

        latest = self.latest(conn)

        extras = {}
        if after:
            extras['after'] = parser.parse(after)
        elif latest:
            extras['after'] = latest[self.order_field]

        if before:
            extras['before'] = parser.parse(before)

        print(
            f"Fetching objects between {extras.get('after')} and {extras.get('before')}")

        batches = self.api_call(client, extras)\
            .iterfetches(retry_on_rate_exceed=True)

        cols = [i.key for i in self.table.columns]

        for batch in batches:
            print(f'Importing a batch of runs ({len(batch)})...')
            for elem in batch:
                if (latest and
                    getattr(elem, self.id_field) == getattr(latest, self.id_field)):
                    print(f'Skipping already imported object {getattr(elem,self.id_field)}.')
                    continue
                data = elem.serialize()
                print(f'Importing object {data[self.id_field]}')
                insert = self.table.insert().values(
                    **{c: process_column(self.table, data, c) for c in cols})
                try:
                    conn.execute(insert)
                except Exception as e:
                    print(f'Error during: {e.orig}')

    def run(self, after, before):
        self.process(after, before)


class ImportRapidProRun(RapidProImport, Command):
    """Imports runs from the RapidPro API"""

    order_field = 'modified_on'
    table = rapidpro.run
    id_field = 'id'

    def get_options(self):
        return [
            Option('flow'),
            Option('-a', '--after', dest='after', default=None),
            Option('-b', '--before', dest='before', default=None),
        ]

    def latest(self, conn):
        q = sqla.select([self.table])\
            .where(rapidpro.run.c.flow__uuid == self.flow)\
            .order_by(sqla.desc(self.table.c[self.order_field]))
        return conn.execute(q).first()

    def api_call(self, client, extras):
        return client.get_runs(flow=self.flow, **extras)

    def run(self, flow, after, before):
        self.flow = flow
        self.process(after, before)


class ImportRapidProContacts(RapidProImport, Command):
    """Imports contacts from the RapidPro API"""

    order_field = 'modified_on'
    table = rapidpro.contact

    def api_call(self, client, extras):
        return client.get_contacts(**extras)
