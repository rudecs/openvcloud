from JumpScale import j
from JumpScale.portal.portal import exceptions
import uuid
ujson = j.db.serializers.ujson
import netaddr

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
    NAMESPACE = 'libcloud'
    CATEGORY = 'libvirtdomain'

    def __init__(self):
        self._te={}
        self._client = j.clients.osis.getByInstance('main')
        self.cache = j.clients.redis.getByInstance('system')
        self.blobdb = self._getKeyValueStore()
        self._models = Models(self._client, 'libvirt', ['node', 'image', 'size', 'resourceprovider', 'vnc', 'macaddress'])
        self.cbmodel = j.clients.osis.getNamespace('cloudbroker')

    def _getKeyValueStore(self):
        if self.NAMESPACE not in self._client.listNamespaces():
            self._client.createNamespace(self.NAMESPACE, template='blob')
        if self.CATEGORY not in self._client.listNamespaceCategories(self.NAMESPACE):
           self._client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
        return j.clients.osis.getCategory(self._client, self.NAMESPACE, self.CATEGORY)

    def listImages(self, resourceid, **kwargs):
        """
        List the available images.
        If no resourceid is provided, all the images are listed.
        resourceid is the id of the resourceprovider.
        param:resourceid optional resourceproviderid.
        result
        """
        query = {}
        if resourceid:
            images = []
            try:
                rp = self._models.resourceprovider.get(resourceid)
            except:
                return []
            query = {'id': {'$in': rp.images}}
        images = self._models.image.search(query)[1:]
        return images

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result
        """
        sizes = self._models.size.search({})[1:]
        return sizes

    def addFreeSubnet(self, subnet, networkid, **kwargs):
        """
        Add a free subnet to the range
        param:subnet subnet in CIDR notation e.g network/subnetmask
        result bool
        """
        key = 'freeipaddresses_%s'% networkid
        try:
            ipaddresses = self.blobdb.get(key)
        except:
            #no list yet
            ipaddresses = []
            self.blobdb.set(key=key, obj=ujson.dumps(ipaddresses))
        net = netaddr.IPNetwork(subnet)
        netrange = net[2:-2]
        for i in netrange:
            if i != net.broadcast:
                ipaddresses.append(str(i))
        self.blobdb.set(key=key, obj=ujson.dumps(ipaddresses))
        return True

    def getFreeIpaddress(self, networkid, **kwargs):
        """
        Get a free Ipaddress from one of ipadress ranges
        param: networkid, id of the network
        result
        """
        key = 'freeipaddresses_%s'% networkid
        ipaddresses = self.blobdb.get(key)
        if ipaddresses:
            ipaddress = ipaddresses.pop(0)
        else:
            ipaddress = None
        self.blobdb.set(key=key, obj=ujson.dumps(ipaddresses))
        return ipaddress

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

    def registerImage(self, name, category, imageid, size, gid, **kwargs):
        image = self._models.image.new()
        image.name = name
        image.type = category
        image.size = size
        image.id = imageid
        image.gid = gid
        image.guid = imageid
        imageid = self._models.image.set(image)[0]
        for resourceprovider in self._models.resourceprovider.search({'gid': gid})[1:]:
            resourceprovider['images'].append(imageid)
            self._models.resourceprovider.set(resourceprovider)
        return imageid

    def removeImage(self, imageid, gid, **kwargs):
        self._models.image.delete(imageid)
        for resourceprovider in self._models.resourceprovider.search({'gid': gid})[1:]:
            if imageid in resourceprovider['images']:
                resourceprovider['images'].remove(imageid)
                self._models.resourceprovider.set(resourceprovider)

    def releaseIpaddress(self, ipaddress, networkid, **kwargs):
        """
        Release a ipaddress.
        param:ipaddress string representing the ipaddres to release
        result bool
        """
        key = 'freeipaddresses_%s'% networkid
        ipaddresses = self.blobdb.get(key)
        ipaddresses.append(ipaddress)
        self.blobdb.set(key=key, obj=ujson.dumps(ipaddresses))
        return True

    def registerNetworkIdRange(self, gid, start, end, **kwargs):
        """
        Add a new network idrange
        param:start start of the range
        param:end end of the range
        result
        """
        key = 'networkids_%s' % gid
        newrange = set(range(int(start), int(end) + 1))
        with self.blobdb.lock(key):
            if self.blobdb.exists(key):
                networkids = set(ujson.loads(self.blobdb.get(key)))
                cloudspaces = self.cbmodel.cloudspace.search({'$fields': ['networkId'],
                                                              '$query': {'status': {'$in': ['DEPLOYED', 'VIRTUAL']},
                                                                         'gid': gid}
                                                              })[1:]
                usednetworkids = {space['networkId'] for space in cloudspaces}
                if usednetworkids.intersection(newrange):
                    raise exceptions.Conflict("Atleast one networkId conflicts with deployed networkids")
            else:
                #  no list yet
                networkids = set()

            networkids.update(newrange)
            self.blobdb.set(key=key, obj=ujson.dumps(list(networkids)))
        return True


    def getFreeNetworkId(self, gid, **kwargs):
        """
        Get a free NetworkId
        result
        """
        key = 'networkids_%s' % gid
        with self.blobdb.lock(key):
            networkids = ujson.loads(self.blobdb.get(key))
            if networkids:
                networkid = networkids.pop(0)
            else:
                networkid = None
            self.blobdb.set(key=key, obj=ujson.dumps(networkids))
        return networkid



    def releaseNetworkId(self, gid, networkid, **kwargs):
        """
        Release a networkid.
        param:networkid int representing the netowrkid to release
        result bool
        """
        key = 'networkids_%s' % gid
        with self.blobdb.lock(key):
            networkids = ujson.loads(self.blobdb.get(key))
            if int(networkid) not in networkids:
                networkids.insert(0,int(networkid))
            self.blobdb.set(key=key, obj=ujson.dumps(networkids))
        return True

    def registerNode(self, id, macaddress, networkid, **kwargs):
        """
        Register some basic node information E.g ipaddress
        param:id id of the node
        result str
        """
        #ipaddress = self.getFreeIpaddress(networkid)
        node = self._models.node.new()
        node.id = id
        #node.ipaddress = ipaddress
        node.macaddress = macaddress
        node.networkid = networkid
        self._models.node.set(node)
        ipaddress = 'Unknown'
        return ipaddress

    def unregisterNode(self, id, **kwargs):
        """
        Unregister a node.
        param:id id of the node to unregister
        result bool
        """
        node = self._models.node.get(id)
        #self.releaseIpaddress(node.ipaddress, node.networkid)
        self._models.node.delete(id)
        return True

    def getNode(self, id, **kwargs):
        """
        Get a node
        param: id of the node to get
        result node
        """
        node = self._models.node.get(id).dump()
        return node

    def listNodes(self, **kwargs):
        """
        List all nodes
        result

        """
        results = self._models.node.search({})[1:]
        nodes = {}
        for res in results:
            node = {'ipaddress': res.get('ipaddress')}
            nodes[res['id']] = node
        return nodes

    def listResourceProviders(self, gid=None, **kwargs):
        query = dict()
        if gid is not None:
            query['gid'] = gid
        results = self._models.resourceprovider.search(query)[1:]
        nodes = {}
        for res in results:
            node = {'cloudunittype': res['cloudUnitType']}
            node['images'] = res['images']
            nodes[res['id']] = node
        return nodes

    def unLinkImage(self, imageid, resourceprovider, **kwargs):
        """
        Unlink a image from a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool
        """
        res = self._models.resourceprovider.get(resourceprovider)
        try:
            res.images.remove(imageid)
        except ValueError:
            pass
        self._models.resourceprovider.set(res)
        return True

    def linkImage(self, imageid, resourceprovider, **kwargs):
        """
        Link a image to a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool
        """
        res = self._models.resourceprovider.get(resourceprovider)
        if not res.images:
            res.images = []
        res.images.append(imageid)
        print res
        self._models.resourceprovider.set(res)
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
