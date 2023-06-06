import threading
import time
from bgservice.libs import api


class WorkerBase(threading.Thread):
    @staticmethod
    def create(config):
        return __class__(config, api.Connection(config))

    def __init__(self, name, interval, apiconnection):
        threading.Thread.__init__(self)
        self.setName(name)
        self._interval = interval
        self._apiconnection = apiconnection

    def task(self, cnt):
        raise NotImplementedError()

    def run(self):
        cnt = 0
        while True:
            task_start = time.time()
            cnt += 1
            self.task(cnt)
            sleep_time = self._interval - (time.time() - task_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
