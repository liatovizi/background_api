from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, Sequence, UniqueConstraint
from sqlalchemy.types import Integer, SmallInteger, BigInteger, String, Text, TIMESTAMP, Enum, DECIMAL
from sqlalchemy import func
import os
import sys
import bcrypt
import hashlib
import base64
sys.path.append("../")

Base = declarative_base()

Double = DECIMAL(28, 8)


class NATAppModel:
    class Languages(Base):
        __tablename__ = 'languages'
        lang_id = Column(Integer, Sequence('languages_lang_id_seq'), primary_key=True)
        label = Column(String(400))
        flag_url = Column(String(250))

    class Messages(Base):
        __tablename__ = 'messages'
        mess_id = Column(Integer, Sequence('messages_mess_id_seq'), primary_key=True)
        lang_id = Column(Integer)
        msg_id = Column(Integer)
        label = Column(String(400))

    class Logins(Base):
        __tablename__ = 'logins'
        login_id = Column(Integer, Sequence('logins_login_id_seq'), primary_key=True)
        user_name = Column(String(54), unique=True)
        password = Column(String(200))
        user_id = Column(Integer, nullable=False)
        num_oflogs = Column(Integer, server_default='0')
        lastlog = Column(TIMESTAMP, server_default=func.now())
        last_login_ip = Column(String(20))

    class Users(Base):
        __tablename__ = 'users'
        __table_args__ = (UniqueConstraint('email_address', name='users_unique_mail'), )
        user_id = Column(Integer, Sequence('users_user_id_seq'), primary_key=True)
        kyc_token = Column(String(54))
        greeting_name = Column(String(54))
        email_address = Column(String(255))
        privileges = Column(SmallInteger, server_default='1')
        locked = Column(SmallInteger, server_default='0')
        email_verify_sent = Column(TIMESTAMP)
        email_resetpwd_sent = Column(TIMESTAMP)
        validity_token = Column(String(200))
        resetpwd_token = Column(String(200))
        verification_level = Column(Integer)
        last_authorized_call = Column(TIMESTAMP)
        newsletter = Column(SmallInteger, server_default='0', nullable=False)
        language = Column(String(4))  #, server_default='hu')
        deleted = Column(SmallInteger, server_default='0')

    class Tokens(Base):
        __tablename__ = 'tokens'
        token_id = Column(Integer, Sequence('tokens_token_id_seq'), primary_key=True)
        user_id = Column(Integer, index=True)
        token = Column(String(30), index=True)
        renew = Column(String(50), index=True)
        created = Column(TIMESTAMP, server_default=func.now())
        valid_to = Column(TIMESTAMP, server_default=func.now())
        renewable_to = Column(TIMESTAMP, server_default=func.now())

    class Maillog(Base):
        __tablename__ = 'maillog'
        maillog_id = Column(Integer, Sequence('maillog_maillog_id_seg'), primary_key=True)
        user_id = Column(Integer, nullable=False)
        template_id = Column(String(100), nullable=False)
        parameters = Column(String(600), nullable=False)
        sent = Column(TIMESTAMP, server_default=func.now(), nullable=False)
        status = Column(SmallInteger, nullable=False)

    class Smslog(Base):
        __tablename__ = 'smslog'
        smslog_id = Column(Integer, Sequence('smslog_smslog_id_seg'), primary_key=True)
        user_id = Column(Integer, nullable=False)
        mobile_num = Column(String(40))
        msg = Column(String(1000), nullable=False)
        sent = Column(TIMESTAMP, server_default=func.now(), nullable=False)
        status = Column(SmallInteger, nullable=False)


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)
    Sess = sessionmaker(bind=migrate_engine)
    session = Sess()
    #    session.add(
    #       NATAppModel.Logins(
    #          login_id=0,
    #         user_name="admin",
    #        password=bcrypt.hashpw(hashlib.sha512("admin".encode('utf-8')).digest(), bcrypt.gensalt(rounds=12)).decode('utf-8'),
    #       user_id=0,
    #      pwdtype='sha512-bcrypt'))
    #    session.add(
    #       NATAppModel.Users(
    #          user_id=0,
    #         greeting_name = "Admin Supremum",
    #        email_address = "admin@admin.admin",
    #       privileges = 0b11111111))

    session.commit()


def downgrade(migrate_engine):
    Base.metadata.drop_all(migrate_engine)
