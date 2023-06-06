import logging

from .scheduled_worker import WorkerBase
from bgservice.epidemicsync_apiservice.apiservice import ApiService
from bgservice.libs import api, epidemicapi
from natapp import db
from natapp.users import models
from sqlalchemy.sql import text as sa_text
import datetime


class EpidemicplaylistWorker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config), epidemicapi.Connection(config))

    def __init__(self, config, apiconnection, epidemicapi):
        WorkerBase.__init__(self, "epidemicplaylist_worker", config.get('EPIDEMICPLAYLIST_DELAY', 100), apiconnection)
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        self._epidemicapi = epidemicapi
        try:
            self._apiservice = ApiService(apiconnection)
        except Exception as e:
            self._logger.error(f'Cannot initialize epidemicplaylist worker, reason: {e}')
            raise KeyError(f'Cannot initialize api object, reason: {e}')

        self._logger.info("initialized.")

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')
        fromhr = self._config.get('EPIDEMICPLAYLIST_WINDOW_FROMHR', 0)
        tohr = self._config.get('EPIDEMICPLAYLIST_WINDOW_TOHR', 0)
        if fromhr < tohr:
            if datetime.datetime.now().hour < fromhr or datetime.datetime.now().hour > tohr:
                self._logger.info(f"skipping update, not in time window {fromhr}-{tohr}")
                return
        elif fromhr > tohr:
            if datetime.datetime.now().hour < fromhr and datetime.datetime.now().hour > tohr:
                self._logger.info(f"skipping update, not in time window {fromhr}-{tohr}")
                return
        resp = self._apiservice.bgservice_getplaylists_api()
        if resp.status_code == 200:
            response = resp.json()
            self._logger.info(f"fetched {len(response['result'])} playlists")
            for pl in response['result']:
                if pl['external_url'] is not None and pl['external_url'] != '':
                    self._logger.info(f'syncing epidemic playlist {pl["playlist_id"]}')
                    entries = None
                    try:
                        entries = list(self._epidemicapi.getplaylist(pl['external_url']))
                    except epidemicapi.InvalidApiReply as e:
                        pass
                    if entries is None:
                        self._logger.error(f"fetching epidemic playlist from {pl['external_url']} failed")
                        continue
                    if entries == []:
                        self._logger.warning(
                            f"fetching epidemic playlist from {pl['external_url']} resulted in an empty list")
                        continue
                    resp = self._apiservice.bgservice_listtracksbyepidemicid_api(
                        list(map(lambda x: {
                            'original_id': x['streaming_id'],
                            'original_id_2': x['track_id']
                        }, entries)))
                    if resp is not None and resp.status_code == 200:
                        response = resp.json()
                        tracks = response['result']
                        self._logger.debug(f"fetched track_ids: {tracks}")
                        mapping = {}
                        for t in tracks:
                            mapping[t['original_id_2']] = t['track_id']
                        entries_keys = list(map(lambda x: x['track_id'], entries))
                        if len(set(entries_keys) - set(mapping.keys())) > 0:
                            self._logger.error(
                                    f"Can't map all epidemic tracks to tracks in the db! playlist: ({pl['playlist_id']}, {pl['name']}) track_ids/original_id_2s: {set(entries_keys) - set(mapping.keys())}"
                            )
                            continue
                        track_ids = [t for t in list(map(mapping.get, entries_keys)) if t is not None]
                        self._logger.debug(f"mapped original_ids: {entries_keys} to track_ids: {track_ids}")

                        if track_ids == pl['tracks']:
                            self._logger.info(f"playlist {pl['playlist_id']} did not change, not updating")
                            continue
                        self._logger.info(f"playlist {pl['playlist_id']} changed, updating tracks {track_ids}")
                        resp = self._apiservice.bgservice_updateplaylist_api(playlist_id=pl['playlist_id'],
                                                                             tracks=track_ids)
                        if resp is not None and resp.status_code == 200:
                            pass
                        else:
                            self._logger.error(f"updating tracks in {pl['playlist_id']} failed")
                    else:
                        self._logger.error(
                            f"fetching tracks by epidemic ids failed for playlist id: {pl['playlist_id']}")
        else:
            self._logger.error(f"fail: {resp.json()}...")
