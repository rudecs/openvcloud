import random
from framework.api import utils

class Qos:
    def __init__(self, api_client):
        self._api = api_client
    
    def limitCPU(self, machineId):
        return self._api.cloudbroker.qos.limitCPU(machineId=machineId)
    
    def resize(self, diskId, size):
        return self._api.cloudbroker.qos.resize(diskId=diskId, size=size)

    def limitIO(self, diskId,**kwargs):
        return self._api.cloudbroker.qos.limitIO(diskId, **kwargs)
    
    def limitInternetBandwith(self, cloudspacId, rate, burst):
        return self._api.cloudbroker.qos.limitInternetBandwith(cloudspacId=cloudspacId, rate=rate, burst=burst)
        
