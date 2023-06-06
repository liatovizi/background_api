from sqlalchemy import Table, MetaData, String, Column, Boolean, Integer, Sequence
from sqlalchemy.dialects.mysql import DATETIME as MYSQLDATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()


class Telemetries(Base):
    __tablename__ = 'telemetries'
    telemetry_id = Column(Integer, Sequence('telemetries_telemetry_id_seq'), primary_key=True)
    instance_id = Column(Integer, nullable=False, index=True, unique=True)
    sw_version = Column(String(24))
    update_channel = Column(String(24))
    mem_free = Column(Integer)
    mem_total = Column(Integer)
    eth0_ip = Column(String(24))
    eth0_netmask = Column(String(24))
    eth0_gw = Column(String(24))
    eth0_dns = Column(String(64))
    eth0_mac = Column(String(24))
    device_timestamp = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))
    modified_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3), onupdate=func.now(3))
    created_at = Column(MYSQLDATETIME(fsp=3), server_default=func.now(3))


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    Base.metadata.create_all(migrate_engine)


def downgrade(migrate_engine):
    Base.metadata.drop_all(migrate_engine)
