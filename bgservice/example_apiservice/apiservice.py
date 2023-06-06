import logging


class ApiService:
    def __init__(self, apiconnection):
        self.apiconnection = apiconnection
        self.logger = logging.getLogger(__name__)

    def bgservice_example_api(self, value):
        try:
            resp = self.apiconnection.post("/bgservice/bgserviceexample",
                                           json={"value": "value123"},
                                           headers={"Content-Type": "application/json"})
        except Exception as e:
            self.logger.exception('Unable to call bgserviceexample api')
            return None

        return resp
