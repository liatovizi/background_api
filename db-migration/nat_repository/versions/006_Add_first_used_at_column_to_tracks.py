from sqlalchemy import Table, MetaData, String, Column, Boolean
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
import datetime


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tracks = Table('tracks', meta, autoload=True)
    PlraylistTracks = Table('playlisttracks', meta, autoload=True)
    first_used_at = Column('first_used_at', MYSQLDATETIME(fsp=3), nullable=True)
    first_used_at.create(Tracks)
    track_ids = [pt.track_id for pt in PlraylistTracks.select(PlraylistTracks).execute().fetchall()]
    Tracks.update().values(first_used_at=datetime.datetime(2020, 1, 1)).where(
        Tracks.c.track_id.in_(track_ids)).execute()


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Tracks = Table('tracks', meta, autoload=True)
    Tracks.c.first_used_at.drop()
