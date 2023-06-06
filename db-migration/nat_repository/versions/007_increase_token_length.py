from sqlalchemy import Table, MetaData, String, Column, Boolean
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tokens = Table('tokens', meta, autoload=True)
    Tokens.c.token.alter(type=String(200), index=True)
    Tokens.c.renew.alter(type=String(200), index=True)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tokens = Table('tokens', meta, autoload=True)
    Tokens.c.token.alter(type=String(30), index=True)
    Tokens.c.renew.alter(type=String(50), index=True)
