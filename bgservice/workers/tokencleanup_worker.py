import logging

from .scheduled_worker import WorkerBase
from bgservice.libs import api
from natapp import db
from natapp.users import models
from sqlalchemy.sql import text as sa_text
from sqlalchemy import and_
from datetime import timedelta
import datetime


class TokencleanupWorker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        WorkerBase.__init__(self, "tokencleanup_worker", config.get('TOKENCLEANUP_DELAY', 100), apiconnection)
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        self._logger.info("initialized.")

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')

        # cleanup tokens
        tokens = db.session.query(models.Tokens).filter(
            and_(models.Tokens.valid_to < datetime.datetime.now() - timedelta(hours=1),
                 models.Tokens.renewable_to < datetime.datetime.now() - timedelta(hours=1)))

        for t in tokens:
            db.session.delete(t)

        db.session.commit()

        self._logger.info(f"cleanup done...")
