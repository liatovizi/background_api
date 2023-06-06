from sqlalchemy import Table, MetaData, String, Column, Boolean
from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Instances = Table('instances', meta, autoload=True)
    class_collective = Column('class_collective', Boolean)
    class_collective.create(Instances)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Instances = Table('instances', meta, autoload=True)
    Instances.c.class_collective.drop()
