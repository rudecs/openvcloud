import random
from framework.api import utils

class Portforwarding:
    def __init__(self,api_client):
        self._api = api_client

    def __get_cloudspace_publicIp(self, cloudspaceId):
        response = self._api.cloudapi.cloudspaces.get(cloudspaceId=cloudspaceId)
        response.raise_for_status
        return response.json()['publicipaddress']

    def list(self, cloudspaceId, **kwargs):
        return self._api.cloudapi.portforwarding.list(cloudspaceId=cloudspaceId, **kwargs)

    def create(self, cloudspaceId, machineId, ** kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'machineId': machineId,
            'publicIp': self.__get_cloudspace_publicIp(cloudspaceId),
            'publicPort': random.randint(1000, 30000),
            'localPort': random.randint(1000, 30000),
            'protocol': random.choice(['udp', 'tcp'])
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.portforwarding.create(** data)

    def delete(self, cloudspaceId, id):
        return self._api.cloudapi.portforwarding.delete(cloudspaceId=cloudspaceId, id=id)

    def deleteByPort(self, cloudspaceId, publicPort, protocol, publicIp=None):
        if not publicIp:
            publicIp = self.__get_cloudspace_publicIp(cloudspaceId)
        
        return self._api.cloudapi.portforwarding.deleteByPort(
            cloudspaceId=cloudspaceId,
            publicIp=publicIp,
            publicPort=publicPort,
            protocol=protocol
        )

    def update(self, cloudspaceId, machineId, id, **kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'machineId': machineId,
            'id': id,
            'publicIp': self.__get_cloudspace_publicIp(cloudspaceId),
            'publicPort': random.randint(1000, 30000),
            'localPort': random.randint(1000, 30000),
            'protocol': random.choice(['udp', 'tcp'])
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.portforwarding.update(** data)

    def updateByPort(self, cloudspaceId, machineId, sourcePublicIp, sourcePublicPort, sourceProtocol, **kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'machineId': machineId,
            'sourcePublicIp':sourcePublicIp,
            'sourcePublicPort':sourcePublicPort,
            'sourceProtocol':sourceProtocol,
            'publicIp': self.__get_cloudspace_publicIp(cloudspaceId),
            'publicPort': random.randint(1000, 30000),
            'localPort': random.randint(1000, 30000),
            'protocol': random.choice(['udp', 'tcp'])
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.portforwarding.update(** data)