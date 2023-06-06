from sqlalchemy import Table, MetaData, String, Column, Boolean, Integer
from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Playlists = Table('playlists', meta, autoload=True)
    class_collective = Column('class_collective', Boolean)
    class_collective.create(Playlists)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Playlists = Table('playlists', meta, autoload=True)
    Playlists.c.class_collective.drop()