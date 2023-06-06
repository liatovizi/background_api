import requests
import json
import logging


class ApiLoginFailed(Exception):
    pass


class RefreshTokenFailed(Exception):
    pass


class InvalidApiConfiguration(Exception):
    pass


class InvalidContentType(Exception):
    pass


class Connection(object):
    def __init__(self, config, dieonerror=True):
        object.__init__(self)
        self._logger = logging.getLogger(__name__)
        try:
            self._api_url = config['API_ENDPOINT']
            self._BGSERVICE_API_USER = config['BGSERVICE_API_USER']
            self._BGSERVICE_API_PASSWORD = config['BGSERVICE_API_PASSWORD']
            self._apilogin()
        except ApiLoginFailed:
            if dieonerror:
                raise
            else:
                self._logger.warning("api login failed")
        self._logger.info(f"Api connection initialized.")

    def _apilogin(self):
        self._access_token = None
        self._refresh_token = None
        try:
            r = requests.post("%s/public/login" % self._api_url,
                              headers={"Content-Type": "application/json"},
                              json={
                                  "username": self._BGSERVICE_API_USER,
                                  "password": self._BGSERVICE_API_PASSWORD
                              })
            self._logger.info("Login response: %s" % r.status_code)
            self._refresh_token = json.loads(r.content)["result"]["refresh_token"]
            self._access_token = json.loads(r.content)["result"]["access_token"]
            self._logger.debug(f"Api auth success. Access token is {self._access_token}")
        except Exception as cerror:
            self._logger.error("DBfeeder login api error: %s" % cerror)
            self._access_token = None
            self._refresh_token = None
            raise ApiLoginFailed(cerror)

    def _refresh(self):
        try:
            r = requests.post("%s/private/refresh" % self._api_url,
                              headers={"Content-Type": "application/json"},
                              json={"refresh_token": self._refresh_token})
            self._access_token = json.loads(r.content)["result"]["access_token"]
            self._refresh_token = json.loads(r.content)["result"]["refresh_token"]
            self._logger.debug(f"Refresh token success. New access token is {self._access_token}")
        except Exception as cerror:
            self._access_token = None
            self._logger.error("Refresh token api error: %s." % cerror)
            raise RefreshTokenFailed(cerror)

    def post(self, url=None, headers=None, timeout=30, **kwargs):
        if url is not None and not url.startswith(self._api_url):
            url = self._api_url + url
        if headers and "Content-Type" in headers and headers["Content-Type"] != "application/json":
            raise InvalidContentType()

        req_headers = {}
        if headers is not None:
            req_headers.update(headers)

        if self._access_token is None:
            self._apilogin()

        req_headers["Content-Type"] = "application/json"
        req_headers["Authorization"] = "Bearer %s" % self._access_token

        r = requests.post(url, headers=req_headers, timeout=timeout, **kwargs)
        if r.status_code in [401, 407]:
            try:
                self._refresh()
            except Exception as cerror:
                self._logger.error("Refresh token failed: %s. Trying to login" % cerror)
                self._apilogin()
            headers["Authorization"] = "Bearer %s" % self._access_token
            r = requests.post(url, headers=headers, **kwargs)
        return r
