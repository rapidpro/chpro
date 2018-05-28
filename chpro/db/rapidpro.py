from sqlalchemy import MetaData, Table, Column, types

metadata = MetaData()

# ToDo: Consider adding migrations
contact = Table('rapidpro_contact', metadata,
                Column('id', types.Integer, primary_key=True),
                Column('uuid', types.String(64)),
                Column('name', types.String(128)),
                Column('groups', types.JSON),
                )

run = Table('rapidpro_run', metadata,
            Column('id', types.Integer, primary_key=True),

            Column('created_on', types.DateTime),
            Column('exit_type', types.String(16)),
            Column('exited_on', types.DateTime),
            Column('modified_on', types.DateTime),
            Column('responded', types.Boolean),

            Column('contact__uuid', types.String(64)),
            Column('flow__uuid', types.String(64)),
            Column('path', types.JSON),
            Column('values', types.JSON),

            )

