from sqlalchemy import Table, MetaData, String, Column, Boolean
from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tracks = Table('tracks', meta, autoload=True)
    original_id_2 = Column('original_id_2', String(64), nullable=True)
    original_id_2.create(Tracks)
    UniqueConstraint('catalog', 'original_id_2', name='catalogoriginalid2_index', table=Tracks).create()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tracks = Table('tracks', meta, autoload=True)
    UniqueConstraint('catalog', 'original_id_2', name='catalogoriginalid2_index', table=Tracks).drop()
    Tracks.c.original_id_2.drop()
