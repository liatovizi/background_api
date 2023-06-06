import logging

from .scheduled_worker import WorkerBase
from bgservice.epidemicsync_apiservice.apiservice import ApiService
from bgservice.libs import api, epidemicimport
from natapp import db
from natapp.users import models
from sqlalchemy.sql import text as sa_text


class EpidemicimportWorker(WorkerBase):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        WorkerBase.__init__(self, "epidemicimport_worker", config.get('EPIDEMICIMPORT_DELAY', 10), apiconnection)
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        try:
            self._apiservice = ApiService(apiconnection)
        except Exception as e:
            self._logger.error(f'Cannot initialize epidemicimport worker, reason: {e}')
            raise KeyError(f'Cannot initialize api object, reason: {e}')

        self._logger.info("initialized.")

    def task(self, cnt):
        self._logger.info(f'cnt={cnt}')

        csvdata = epidemicimport.parse_epidemic_csv(self._config['EPIDEMIC_IMPORT_CSV'])

        self._logger.debug(f"loaded {len(csvdata)} from CSV file")

        original_trackids = list(
            map(lambda x: {
                'original_id': x['streaming_id'],
                'original_id_2': x['track_id']
            }, csvdata))

        oids = set()

        for i in range(len(original_trackids)):
            if i % 1000 == 999 or i == len(original_trackids) - 1:
                self._logger.info(f"checking loaded tracks {1000*(i//1000)}-{i} in the DB...")
                resp = self._apiservice.bgservice_listtracksbyepidemicid_api(
                    original_trackids[(i // 1000) * 1000:i + 1])
                if resp is not None and resp.status_code == 200:
                    response = resp.json()
                    for t in response['result']:
                        oids.add(t['original_id'])
                else:
                    self._logger.error(f"failed to fetch already imported tracks form DB")
                    return

        for track in csvdata:
            if track['streaming_id'] not in oids:
                if 'sha256' not in track or track['sha256'] is None or track['sha256'] == "":
                    self._logger.error(f"track with missing sha256 in the tracks file: {track['streaming_id']}")
                    continue
                params = {
                    'original_id': track['streaming_id'],
                    'original_id_2': track['track_id'],
                    'title': track['title'],
                    'composer_id': track['composer_id'],
                    'composer_name': track['composer_name'],
                    'moods': track['moods_str'],
                    'genres': track['genres_str'],
                    'metadata_tags': track['metadata_tags_str'],
                    'tempo_bpm': int(track['tempo_bpm']),
                    'energy_level': track['energy_level'],
                    'release_date': track['release_date'],
                    'duration': round(float(track['duration'])),
                    'url': track['url'],
                    'sha256': track['sha256']
                }
                resp = self._apiservice.bgservice_addepidemictrack_api(**params)
                if resp.status_code == 200:
                    self._logger.info(
                        f"imported track with epidemic streaming id {track['streaming_id']}, got id: {resp.json()['result']['track_id']}"
                    )
                else:
                    self._logger.error(f" fail: {track['streaming_id']} {resp.json()}...")
                    self._logger.debug("{params}...")
            else:
                self._logger.debug(f'skipping import of already imported track: {track["streaming_id"]}')
