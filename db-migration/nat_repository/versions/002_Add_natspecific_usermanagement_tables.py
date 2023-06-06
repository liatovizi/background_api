from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, Sequence, UniqueConstraint
from sqlalchemy.types import Integer, SmallInteger, BigInteger, String, Boolean, Text, TIMESTAMP, Enum, DECIMAL, Binary, DATETIME
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
from sqlalchemy import func, false
import os
import sys
import bcrypt
import hashlib
import base64
import datetime
sys.path.append("../")

Base = declarative_base()

Double = DECIMAL(28, 8)


class NATAppModel:
    class Instances(Base):
        __tablename__ = 'instances'
        __table_args__ = (UniqueConstraint('activation_code', name='instances activation_code'), )
        instance_id = Column(Integer, Sequence('instances_id_seq'), primary_key=True)
        location_id = Column(Integer, nullable=True)
        activation_code = Column(String(100))
        label = Column(String(64), nullable=True)
        token = Column(String(150), nullable=False)
        status = Column(String(24), nullable=False)
        last_authorized_call = Column(MYSQLDATETIME(fsp=3))
        update_channel = Column(String(24))
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))

    class Locations(Base):
        __tablename__ = 'locations'
        location_id = Column(Integer, Sequence('locations_id_seq'), primary_key=True)
        user_id = Column(Integer, nullable=False)
        name = Column(String(128), nullable=False)
        country = Column(String(64))
        state = Column(String(64))
        city = Column(String(64))
        zip = Column(String(20))
        address = Column(String(128))
        instance_count = Column(Integer, default=0)
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))

    class LocationUsers(Base):
        __tablename__ = 'locationusers'
        locationuser_id = Column(Integer, Sequence('locationuser_id_seq'), primary_key=True)
        location_id = Column(Integer, nullable=False, index=True)
        user_id = Column(Integer, nullable=False, index=True)
        label = Column(String(128))
        pin_code = Column(String(32))
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))
        __table_args__ = (UniqueConstraint('location_id', 'user_id', name='userlocation_index'), )


# Track metadata
#Id	Title	MetadataTags	Genres	Moods	TempoBPM	EnergyLevel	HasVocals	Releasedate	ComposerId	ComposerName

    class Tracks(Base):
        __tablename__ = 'tracks'
        __table_args__ = (UniqueConstraint('catalog', 'original_id', name='catalogoriginalid_index'), )
        track_id = Column(Integer, Sequence('track_id_seq'), primary_key=True)
        user_id = Column(Integer)
        original_id = Column(String(64))
        catalog = Column(String(32), index=True)
        title = Column(String(128), index=True)
        composer_id = Column(String(64), index=True)
        composer_name = Column(String(128), index=True)
        #        metadata_tags = Column(String(255))
        #        genres = Column(String(255))
        #        moods = Column(String(255))
        tempo_bpm = Column(Integer, index=True)
        energy_level = Column(String(32), index=True)
        release_date = Column(MYSQLDATETIME)
        url = Column(String(128))
        duration = Column(Integer)
        sha256 = Column(String(64))
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))

    class TrackTags(Base):
        __tablename__ = 'tracktags'
        __table_args__ = (UniqueConstraint('track_id', 'tag_id', name='track_id_tag_id_index'), )
        tracktag_id = Column(Integer, Sequence('tracktag_id_seq'), primary_key=True)
        track_id = Column(Integer, nullable=False, index=True)
        tag_id = Column(Integer, nullable=False, index=True)

    class Tags(Base):
        __tablename__ = 'tags'
        __table_args__ = (UniqueConstraint('type', 'label', 'sublabel', name='type_label_sublabel_index'), )
        tag_id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
        type = Column(String(32), nullable=False, index=True)
        label = Column(String(64), nullable=False, index=True)
        sublabel = Column(String(64), nullable=True, index=True)

    class Playlists(Base):
        __tablename__ = 'playlists'
        playlist_id = Column(Integer, Sequence('playlist_id_seq'), primary_key=True)
        name = Column(String(128), nullable=False)
        description = Column(String(255))
        user_id = Column(Integer)
        external_url = Column(String(128))
        meta = Column(String(255), nullable=False)
        system = Column(Boolean, default=False)
        deleted_at = Column(MYSQLDATETIME(fsp=3))
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))
        __table_args__ = ()

    class PlaylistTracks(Base):
        __tablename__ = 'playlisttracks'
        playlisttrack_id = Column(Integer, Sequence('playlisttrac_id_seq'), primary_key=True)
        playlist_id = Column(Integer, index=True, nullable=False)
        track_id = Column(Integer, index=True, nullable=False)
        rank = Column(Integer, nullable=False)
        created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))
        __table_args__ = ()


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)
    Sess = sessionmaker(bind=migrate_engine)
    session = Sess()
    session.commit()
    pass


def downgrade(migrate_engine):
    Base.metadata.drop_all(migrate_engine)
    pass
