from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy.sql.expression import tuple_, or_
import sqlalchemy.types as types
from sqlalchemy.dialects.mysql import DATETIME
import datetime

Model = declarative_base()
Double = DECIMAL(28, 8)


class TimestampMS(types.TypeDecorator):
    #impl = types.DATETIME
    impl = DATETIME

    def process_bind_param(self, value, dialect):
        if value == None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        return datetime.datetime.utcfromtimestamp(value / 1000)

    def process_result_value(self, value, dialect):
        if value == None:
            return None
        return round(value.timestamp() * 1000)
