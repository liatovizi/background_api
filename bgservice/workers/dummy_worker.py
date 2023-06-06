import threading
import time
import decimal
import logging

from natapp import db
from bgservice.example_apiservice.apiservice import ApiService

from bgservice.libs import api


# dummmy worker - api access example
class DummyWorker(threading.Thread):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, config, apiconnection):
        threading.Thread.__init__(self)
        self.setName('dummy_worker')
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._apiconnection = apiconnection
        try:
            self._apiservice = ApiService(apiconnection)
        except Exception as e:
            self._logger.error(f'Cannot initialize dummy worker, reason: {e}')
            raise KeyError(f'Cannot initialize dummy object, reason: {e}')

        self._logger.info("initialized.")

    def run(self):
        while True:
            self._logger.info("dummy run start...")
            resp = self._apiservice.bgservice_example_api("almafa")
            if resp.status_code == 200:
                self._logger.info(f"dummy run end: {resp.json()['result']['value']}...")
            time.sleep(5)
