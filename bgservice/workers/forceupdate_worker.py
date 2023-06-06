import logging

from .scheduled_worker import WorkerBase
from bgservice.epidemicsync_apiservice.apiservice import ApiService
from bgservice.libs import api, epidemicapi
from natapp import db
from natapp.nat import models
from sqlalchemy.sql import text as sa_text
import datetime


class ForceUpdateWorker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        WorkerBase.__init__(self, "forceupdate_worker", 2000, apiconnection)
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        try:
            self._apiservice = ApiService(apiconnection)
        except Exception as e:
            self._logger.error(f'Cannot initialize forceupdate worker, reason: {e}')
            raise KeyError(f'Cannot initialize api object, reason: {e}')

        self._logger.info("initialized.")

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')
        hour = self._config.get('FORCE_CONTENTUPDATE_HOUR', 2)
        if datetime.datetime.now().hour == hour:
            # cleanup tokens
            db.session.query(models.Instances).update({'force_content_update': 3}, synchronize_session=False)
            db.session.commit()