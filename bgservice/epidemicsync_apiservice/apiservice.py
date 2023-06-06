import logging


class ApiService:
    def __init__(self, apiconnection):
        self.apiconnection = apiconnection
        self.logger = logging.getLogger(__name__)

    def bgservice_addepidemictrack_api(self, original_id, original_id_2, title, composer_id, composer_name,
                                       metadata_tags, genres, moods, tempo_bpm, energy_level, release_date, url,
                                       duration, sha256):
        try:
            resp = self.apiconnection.post("/bgservice/addepidemictrack",
                                           json={
                                               'original_id': original_id,
                                               'original_id_2': original_id_2,
                                               'title': title,
                                               'composer_id': composer_id,
                                               'composer_name': composer_name,
                                               'metadata_tags': metadata_tags,
                                               'genres': genres,
                                               'moods': moods,
                                               'tempo_bpm': tempo_bpm,
                                               'energy_level': energy_level,
                                               'release_date': release_date,
                                               'url': url,
                                               'duration': duration,
                                               'sha256': sha256
                                           },
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to call addepidemictrack api')
            return None

        return resp

    def bgservice_getplaylists_api(self):
        try:
            resp = self.apiconnection.post("/bgservice/getplaylists",
                                           json={},
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to call getplaylists api')
            return None

        return resp

    def bgservice_listplaylists_api(self, deleted=False):
        try:
            resp = self.apiconnection.post("/bgservice/listplaylists",
                                           json={'deleted': deleted},
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to call listplaylists api')
            return None

        return resp

    def bgservice_listtracksbyepidemicid_api(self, tracks):
        try:
            resp = self.apiconnection.post("/bgservice/listtracksbyepidemicid",
                                           json={'tracks': tracks},
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to call list tracks by epidemic id')
            return None

        return resp

    def bgservice_updateplaylist_api(self, playlist_id, tracks):
        try:
            resp = self.apiconnection.post("/bgservice/updateplaylist",
                                           json={
                                               'tracks': tracks,
                                               'playlist_id': playlist_id
                                           },
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to update epidemic playlist tracks')
            return None

        return resp

    def bgservice_removeplaylist_api(self, playlist_id):
        try:
            resp = self.apiconnection.post("/bgservice/removeplaylist",
                                           json={'playlist_id': playlist_id},
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to remove epidemic playlist')
            return None

        return resp