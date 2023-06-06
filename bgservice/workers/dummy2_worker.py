import logging

from .scheduled_worker import WorkerBase
from bgservice.libs import api
from natapp import db
from natapp.users import models
from sqlalchemy.sql import text as sa_text


# dummmy worker - db access example
class Dummy2Worker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        WorkerBase.__init__(self, "dummy2_worker", 10, apiconnection)
        self._logger = logging.getLogger(__name__)

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')
        u = db.session.query(models.Logins).first()
        self._logger.info(f"dummy2... {u}")
