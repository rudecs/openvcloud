import random
from framework.api import utils

class Iaas:
    def __init__(self, api_client):
        self._api = api_client

    def addExternalIPs(self,externalnetworkId, startip, endip):
        return self._api.cloudbroker.iaas.addExternalIPs(externalnetworkId=externalnetworkId, startip=startip, endip=endip)

    def changeIPv4Gateway(self, externalnetworkId, gateway):
        return self._api.cloudbroker.iaas.changeIPv4Gateway(externalnetworkId=externalnetworkId, gateway=gateway)

    def deleteExternalNetwork(self, externalnetworkId):
        return self._api.cloudbroker.iaas.deleteExternalNetwork(externalnetworkId=externalnetworkId)

    def deleteSize(self, sizeid):
        return self._api.cloudbroker.iaas.deleteSize(size_id=sizeid)
  
    def editPingIps(self, externalnetworkId, pingips):
        return self._api.cloudbroker.iaas.editPingIps(externalnetworkId=externalnetworkId, pingips=pingips)
  
    def removeExternalIP(self, externalnetworkId, ip):
        return self._api.cloudbroker.iaas.removeExternalIP(externalnetworkId=externalnetworkId, ip=ip)

    def removeExternalIPs(self, externalnetworkId, freeips):
        return self._api.cloudbroker.iaas.removeExternalIP(externalnetworkId=externalnetworkId, freeips=freeips)

 
        