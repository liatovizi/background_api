from sqlalchemy import Table, MetaData, String, Column, Boolean, Integer, Sequence, BigInteger
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Telemetries = Table('telemetries', meta, autoload=True)
    Telemetries.c.mem_free.alter(type=BigInteger)
    Telemetries.c.mem_total.alter(type=BigInteger)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Telemetries = Table('telemetries', meta, autoload=True)
    Telemetries.c.mem_free.alter(type=Integer)
    Telemetries.c.mem_total.alter(type=Integer)
