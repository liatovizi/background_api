import logging

from .scheduled_worker import WorkerBase
from bgservice.epidemicsync_apiservice.apiservice import ApiService
from bgservice.libs import api, epidemicapi
from natapp import db
from natapp.users import models
from sqlalchemy.sql import text as sa_text
import datetime


class PlaylistcleanupWorker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        WorkerBase.__init__(self, "playlistcleanup_worker", config.get('PLAYLISTCLEANUP_DELAY', 100), apiconnection)
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        try:
            self._apiservice = ApiService(apiconnection)
        except Exception as e:
            self._logger.error(f'Cannot initialize playlistcleanup worker, reason: {e}')
            raise KeyError(f'Cannot initialize api object, reason: {e}')

        self._logger.info("initialized.")

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')
        resp = self._apiservice.bgservice_listplaylists_api(deleted=True)
        if resp.status_code == 200:
            response = resp.json()
            self._logger.info(f"fetched {len(response['result'])} playlists")
            for pl in response['result']:
                if pl['deleted_at'] is not None and pl['deleted_at'] < (datetime.datetime.now() -
                                                                        datetime.timedelta(days=14)).timestamp() * 1000:
                    self._logger.info(f'removing expired playlist {pl["playlist_id"]}')
                    resp = self._apiservice.bgservice_removeplaylist_api(playlist_id=pl["playlist_id"])
                    if resp is not None and resp.status_code == 200:
                        pass
                    else:
                        self._logger.error(f"failed to remove playlist {pl['playlist_id']}")
        else:
            self._logger.error(f"fail: {resp.json()}...")
