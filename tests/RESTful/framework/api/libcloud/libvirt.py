import random

class Libvirt:
    def __init__(self, api_client):
        self._api = api_client

    def getFreeMacAddress(self, gid):
        return self._api.libcloud.libvirt.getFreeMacAddress(gid=gid)

    def getFreeNetworkId(self, gid):
        return self._api.libcloud.libvirt.getFreeNetworkId(gid=gid)

    def listVNC(self, gid):
        return self._api.libcloud.libvirt.listVNC(gid=gid)

    def registerNetworkIdRange(self, gid, ** kwargs):
        data = {
            'gid':gid,
            'start': random.randint(1, 1000),
            'end': random.randint(1000, 2000)
        }
        data.update(** kwargs)
        return data, self._api.libcloud.libvirt.registerNetworkIdRange(** data)

    def registerVNC(self, gid, url):
        return self._api.libcloud.libvirt.registerVNC(gid=gid, url=url)

    def releaseNetworkId(self, gid, networkid):
        return self._api.libcloud.libvirt.releaseNetworkId(gid=gid, networkid=networkid)

    def retreiveInfo(self, key, reset=False):
        return self._api.libcloud.libvirt.retreiveInfo(key=key, reset=reset)

    def storeInfo(self, data, timeout=0):
        return self._api.libcloud.libvirt.storeInfo(data=data, timeout=timeout)

    