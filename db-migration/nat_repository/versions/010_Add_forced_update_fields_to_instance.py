from sqlalchemy import Table, MetaData, String, Column, Boolean, Integer
from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Instances = Table('instances', meta, autoload=True)
    force_sw_update = Column('force_sw_update', Integer)
    force_content_update = Column('force_content_update', Integer)
    force_sw_update.create(Instances)
    force_content_update.create(Instances)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Instances = Table('instances', meta, autoload=True)
    Instances.c.force_sw_update.drop()
    Instances.c.force_content_update.drop()
