import random
from framework.api import utils

class Alerts:
    def __init__(self, api_client):
        self._api = api_client

    def escalate(self, alert, **kwargs):
        return self._api.system.alert.escalate(alert=alert, ** kwargs)

    def update(self, alert, **kwargs):
        data = {
            'alert': alert,
            'state': random.choice(['NEW', 'ALERT', 'ACCEPTED', 'RESOLVED', 'UNRESOLVED', 'CLOSED']),
            'username':'',
            'comment': ''
        }
        data.update(**kwargs)
        return data, self._api.system.alert.update(** data)