from natapp.dbbase import *


class Instances(Model):
    __tablename__ = 'instances'
    __table_args__ = (UniqueConstraint('activation_code', name='instances activation_code'), )
    instance_id = Column(Integer, Sequence('instances_id_seq'), primary_key=True)
    location_id = Column(Integer, nullable=True)
    activation_code = Column(String(100))
    label = Column(String(64), nullable=True)
    token = Column(String(150), nullable=False)
    status = Column(String(24), nullable=False)
    class_collective = Column(Boolean)
    update_channel = Column(String(24))
    force_sw_update = Column(Integer, nullable=True)
    force_content_update = Column(Integer, nullable=True)
    last_authorized_call = Column(TimestampMS(fsp=3))
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))


class Locations(Model):
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
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))


class Telemetries(Model):
    __tablename__ = 'telemetries'
    telemetry_id = Column(Integer, Sequence('telemetries_telemetry_id_seq'), primary_key=True)
    instance_id = Column(Integer, nullable=False, index=True, unique=True)
    sw_version = Column(String(24))
    update_channel = Column(String(24))
    mem_free = Column(BigInteger)
    mem_total = Column(BigInteger)
    eth0_ip = Column(String(24))
    eth0_netmask = Column(String(24))
    eth0_gw = Column(String(24))
    eth0_dns = Column(String(64))
    eth0_mac = Column(String(24))
    device_timestamp = Column(TimestampMS(fsp=3), server_default=func.now(3))
    modified_at = Column(TimestampMS(fsp=3), server_default=func.now(3), onupdate=func.now(3))
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))


class LocationUsers(Model):
    __tablename__ = 'locationusers'
    __table_args__ = (UniqueConstraint('location_id', 'user_id', name='userlocation_index'), )
    locationuser_id = Column(Integer, Sequence('locationusers_id_seq'), primary_key=True)
    location_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    pin_code = Column(String(32))
    label = Column(String(128))
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))


class Tracks(Model):
    __tablename__ = 'tracks'
    __table_args__ = (
        UniqueConstraint('catalog', 'original_id', name='catalogoriginalid_index'),
        UniqueConstraint('catalog', 'original_id_2', name='catalogoriginalid2_index'),
    )
    track_id = Column(Integer, Sequence('track_id_seq'), primary_key=True)
    user_id = Column(Integer)
    # streaming id for epidemic
    original_id = Column(String(64))
    # track id for epidemic
    original_id_2 = Column(String(64))
    catalog = Column(String(32))
    title = Column(String(128))
    composer_id = Column(String(64))
    composer_name = Column(String(128))
    #metadata_tags = Column(String(255))
    #genres = Column(String(255))
    #moods = Column(String(255))
    tempo_bpm = Column(Integer)
    energy_level = Column(String(32))
    release_date = Column(TimestampMS())
    url = Column(String(128))
    duration = Column(Integer)
    sha256 = Column(String(64))
    first_used_at = Column(TimestampMS(fsp=3))
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))


class TrackTags(Model):
    __tablename__ = 'tracktags'
    __table_args__ = (UniqueConstraint('track_id', 'tag_id', name='track_id_tag_id_index'), )
    tracktag_id = Column(Integer, Sequence('tracktag_id_seq'), primary_key=True)
    track_id = Column(Integer, nullable=False, index=True)
    tag_id = Column(Integer, nullable=False, index=True)


class Tags(Model):
    __tablename__ = 'tags'
    __table_args__ = (UniqueConstraint('type', 'label', 'sublabel', name='type_label_sublabel_index'), )
    tag_id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    type = Column(String(32), nullable=False)
    label = Column(String(64), nullable=False)
    sublabel = Column(String(64), nullable=True)


class Playlists(Model):
    __tablename__ = 'playlists'
    playlist_id = Column(Integer, Sequence('playlist_id_seq'), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(255))
    user_id = Column(Integer)
    external_url = Column(String(128))
    meta = Column(String(255), nullable=False)
    system = Column(Boolean, default=False)
    hidden = Column('hidden', Boolean(), default=False, server_default='0', nullable=False)
    class_collective = Column(Boolean(), default=False)
    deleted_at = Column(TimestampMS(fsp=3))
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))
    __table_args__ = ()


class PlaylistTracks(Model):
    __tablename__ = 'playlisttracks'
    playlisttrack_id = Column(Integer, Sequence('playlisttrac_id_seq'), primary_key=True)
    playlist_id = Column(Integer, index=True, nullable=False)
    track_id = Column(Integer, index=True, nullable=False)
    rank = Column(Integer, nullable=False)
    created_at = Column(TimestampMS(fsp=3), server_default=func.now(3))
    __table_args__ = ()
