from sqlalchemy import Table, MetaData, String, Column, Boolean


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Playlists = Table('playlists', meta, autoload=True)
    hidden = Column('hidden', Boolean(), default=False, server_default='0', nullable=False)
    hidden.create(Playlists)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Playlists = Table('playlists', meta, autoload=True)
    Playlists.c.hidden.drop()