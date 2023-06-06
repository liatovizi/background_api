import requests
import json
import logging
import re


class InvalidApiReply(Exception):
    pass


class Connection(object):
    def __init__(self, config, dieonerror=True):
        object.__init__(self)
        self._logger = logging.getLogger(__name__)
        try:
            True
        except ApiLoginFailed:
            if dieonerror:
                raise
            else:
                self._logger.warning("api login failed")
        self._logger.info(f"Api connection initialized.")

    def _do_request(self, url, data=None, timeout=15, **kwargs):
        method = requests.get
        if data is not None:
            method = requests.post
        r = method(url,
                   headers={
                       'Accept': '*/*',
                       'Referer': 'https://www.epidemicsound.com/login/',
                       'Host': 'www.epidemicsound.com',
                       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
                   },
                   cookies={},
                   data=data,
                   timeout=timeout,
                   **kwargs)
        return r

    def getplaylist(self, playlist_url):
        url = 'https://www.epidemicsound.com/cloudcasting/playlist/' + re.sub(
            r".*/playlists{0,1}/+([0-9a-zA-Z]+)/{0,1}$", r"\1", playlist_url)
        r = self._do_request(url)
        if r.status_code not in [200, 201] or r.headers['Content-Type'] != 'application/json':
            raise InvalidApiReply("Invalid ecpidemic reply status code!")

        try:
            x = r.json()

            if x is not None and 'entries' in x:
                return list(
                    map(
                        lambda xx: {
                            'streaming_id': None if xx.get('streamingId') in [None, 0] else str(xx['streamingId']),
                            'track_id': None if xx.get('trackId') in [None, 0] else str(xx['trackId'])
                        }, x['entries']))
        except Exception as cerror:
            self._logger.error(f"Epidemic getplaylist api error: {cerror}")
            self._access_token = None
            self._refresh_token = None
            raise InvalidApiReply(cerror)
