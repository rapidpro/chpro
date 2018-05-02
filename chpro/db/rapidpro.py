from sqlalchemy import MetaData, Table, Column, types

metadata = MetaData()

"""
{'contact': {'name': 'Shibinda Sikasukwe',
  'uuid': '9ec03025-0366-46a4-aa36-824282d01b3e'},
 'created_on': '2018-05-02T12:40:51.041265Z',
 'exit_type': 'expired',
 'exited_on': '2018-05-02T14:31:56.391465Z',
 'flow': {'name': 'Reasons of Vaccine Missing - step2',
  'uuid': '7a376c32-fc78-49c9-b200-2f462efb7b10'},
 'id': 644256569,
 'modified_on': '2018-05-02T14:31:56.391465Z',
 'path': [{'node': '9f2a76f4-a247-48e5-996f-947d0ffca874',
   'time': '2018-05-02T12:40:51.063833Z'},
  {'node': 'a0a643a5-7b83-45e6-a492-5e1e83242ea6',
   'time': '2018-05-02T12:40:51.351509Z'}],
 'responded': False,
 'start': None,
 'values': {}}
 """

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
