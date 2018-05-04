from sqlalchemy import MetaData, Table, Column, types

metadata = MetaData()

contact = Table('rapidpro_contact', metadata,
                Column('id', types.Integer, primary_key=True),

                )

run = Table('rapidpro_run', metadata,
            Column('id', types.Integer, primary_key=True),
            Column('created_on', types.DateTime),
            Column('exit_type', types.String(16)),
            Column('exited_on', types.DateTime),
            Column('modified_on', types.DateTime),
            Column('responded', types.Boolean),
            )

