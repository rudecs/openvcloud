from JumpScale import j
from JumpScale.portal.portal import exceptions
import uuid
import netaddr
ujson = j.db.serializers.ujson


class Models(object):
    def __init__(self, client, namespace, categories):
        if namespace not in client.listNamespaces():
            client.createNamespace(namespace, template='modelobjects')
        osiscats = client.listNamespaceCategories(namespace)
        for category in categories:
            if category not in osiscats:
                client.createNamespaceCategory(namespace, category)
            setattr(self, category, j.clients.osis.getCategory(client, namespace, category))


class libcloud_libvirt(object):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    """
    def __init__(self):
        self._te = {}
        self._client = j.clients.osis.getByInstance('main')
        self.cache = j.clients.redis.getByInstance('system')
        self._models = Models(self._client, 'libvirt', ['vnc', 'macaddress', 'networkids'])
        self.cbmodel = j.clients.osis.getNamespace('cloudbroker')

    def getFreeMacAddress(self, gid, **kwargs):
        """
        Get a free macaddres in this libvirt environment
        result
        """
        mac = self._models.macaddress.set(key=gid, obj=1)
        firstmac = netaddr.EUI('52:54:00:00:00:00')
        newmac = int(firstmac) + mac
        macaddr = netaddr.EUI(newmac)
        macaddr.dialect = netaddr.mac_eui48
        return str(macaddr).replace('-', ':').lower()

    def registerNetworkIdRange(self, gid, start, end, **kwargs):
        """
        Add a new network idrange
        param:start start of the range
        param:end end of the range
        result
        """
        newrange = set(range(int(start), int(end) + 1))
        if self._models.networkids.exists(gid):
            cloudspaces = self.cbmodel.cloudspace.search({'$fields': ['networkId'],
                                                          '$query': {'status': {'$in': ['DEPLOYED', 'VIRTUAL']},
                                                                     'gid': gid}
                                                          })[1:]
            usednetworkids = {space['networkId'] for space in cloudspaces}
            if usednetworkids.intersection(newrange):
                raise exceptions.Conflict("Atleast one networkId conflicts with deployed networkids")
            self._models.networkids.updateSearch({'id': gid},
                                                 {'$addToSet': {'networkids': {'$each': newrange}}})
        else:
            networkids = {'id': gid, 'networkids': newrange}
            self._models.networkids.set(networkids)
        return True

    def getFreeNetworkId(self, gid, **kwargs):
        """
        Get a free NetworkId
        result
        """
        for netid in self._models.networkids.get(gid).networkids:
            res = self._models.networkids.updateSearch({'id': gid},
                                                       {'$pull': {'networkids': netid}})
            if res['nModified'] == 1:
                return netid

    def releaseNetworkId(self, gid, networkid, **kwargs):
        """
        Release a networkid.
        param:networkid int representing the netowrkid to release
        result bool
        """
        self._models.networkids.updateSearch({'id': gid},
                                             {'$addToSet': {'networkids': networkid}})
        return True

    def registerVNC(self, url, gid, **kwargs):
        vnc = self._models.vnc.new()
        vnc.url = url
        vnc.gid = gid
        return self._models.vnc.set(vnc)

    def retreiveInfo(self, key, reset=False, **kwargs):
        """
        get info
        param:key key of data
        result dict
        """
        key = str(key)
        info = self.cache.get(key)
        if reset:
            self.cache.delete(key)
        if info:
            info = ujson.loads(info)
        return info

    def storeInfo(self, data, timeout, **kwargs):
        """
        store info for period of time
        param:data store data for period of time
        param:timeout timeout for data
        result str
        """
        key = str(uuid.uuid4())
        self.cache.set(key, ujson.dumps(data), timeout)
        return key

    def listVNC(self, gid, **kwargs):
        """
        list vnc urls
        result
        """
        gid = int(gid)
        results = self._models.vnc.search({'gid': gid})[1:]
        return [res['url'] for res in results]
