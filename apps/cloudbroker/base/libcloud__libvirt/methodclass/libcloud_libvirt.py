from JumpScale import j
import JumpScale.grid.osis
import uuid
ujson = j.db.serializers.ujson
import memcache
import netaddr

class Models(object):
    def __init__(self, client, namespace, categories):
        if namespace not in client.listNamespaces():
            client.createNamespace(namespace, template='modelobjects')
        osiscats = client.listNamespaceCategories(namespace)
        for category in categories:
            if category not in osiscats:
                client.createNamespaceCategory(namespace, category)
            setattr(self, category, j.core.osis.getClientForCategory(client, namespace, category))

class libcloud_libvirt(object):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    """
    NAMESPACE = 'libcloud'
    CATEGORY = 'libvirtdomain'

    def __init__(self):
        self._te={}
        self._client = j.core.osis.getClient(user='root')
        self.cache = memcache.Client(['localhost:11211'])
        self.blobdb = self._getKeyValueStore()
        self._models = Models(self._client, 'libvirt', ['node', 'image', 'size', 'resourceprovider', 'vnc'])

    def _getKeyValueStore(self):
        if self.NAMESPACE not in self._client.listNamespaces():
            self._client.createNamespace(self.NAMESPACE, template='blob')
        if self.CATEGORY not in self._client.listNamespaceCategories(self.NAMESPACE):
           self._client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
        return j.core.osis.getClientForCategory(self._client, self.NAMESPACE, self.CATEGORY)

    def listImages(self, resourceid, **kwargs):
        """
        List the available images.
        If no resourceid is provided, all the images are listed.
        resourceid is the id of the resourceprovider.
        param:resourceid optional resourceproviderid.
        result
        """
        if resourceid:
            images = []
            try:
                rp = self._models.resourceprovider.get(resourceid)
            except:
                return []
            for i in rp.images:
                images.append(j.code.object2dict(self._models.image.get(i)))
            return images
        query = {'fields': ['id', 'name', 'description', 'type', 'UNCPath', 'size', 'extra']}
        results = self._models.image.search(query)['result']
        images = [res['fields'] for res in results]
        return images

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result
        """
        query = {'fields': ['id', 'name', 'vcpus', 'memory', 'disk']}
        results = self._models.size.search(query)['result']
        sizes = [res['fields'] for res in results]
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

    def getFreeMacAddress(self, **kwargs):
        """
        Get a free macaddres in this libvirt environment
        result
        """
        try:
            lastMac = self.blobdb.get('lastmacaddress')
        except:
            newmacaddr = netaddr.EUI('52:54:00:00:00:00')
            self.blobdb.set(key='lastmacaddress', obj=ujson.dumps(int(newmacaddr)))
            lastMac = int(newmacaddr)
        newmacaddr = lastMac + 1
        macaddr = netaddr.EUI(newmacaddr)
        macaddr.dialect = netaddr.mac_unix
        self.blobdb.set(key='lastmacaddress', obj=ujson.dumps(newmacaddr))
        return str(macaddr)

    

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

    def registerNetworkIdRange(self, start, end, **kwargs):
        """
        Add a new network idrange
        param:start start of the range
        param:end end of the range
        result 
        """
        try:
           networkids  = self.blobdb.get('networkids')
        except:
            #no list yet
            networkids = []
            self.blobdb.set(key='networkids', obj=ujson.dumps(networkids))
        toappend = [i for i in range(int(start), int(end) + 1) if i not in networkids]
        networkids = networkids + toappend
        self.blobdb.set(key='networkids', obj=ujson.dumps(networkids))
        return True


    def getFreeNetworkId(self, **kwargs):
        """
        Get a free NetworkId
        result 
        """
        networkids = self.blobdb.get('networkids')
        if networkids:
            networkid = networkids.pop(0)
        else:
            networkid = None
        self.blobdb.set(key='networkids', obj=ujson.dumps(networkids))
        return networkid



    def releaseNetworkId(self, networkid, **kwargs):
        """
        Release a networkid.
        param:networkid int representing the netowrkid to release
        result bool
        """
        networkids = self.blobdb.get('networkids')
        networkids.insert(0,int(networkid))
        self.blobdb.set(key='networkids', obj=ujson.dumps(networkids))
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
        node = self._models.node.get(id)
        return node

    def listNodes(self, **kwargs):
        """
        List all nodes
        result

        """
        query = {'fields': ['id', 'ipaddress', 'macaddress']}
        results = self._models.node.search(query)['result']
        nodes = {}
        for res in results:
            node = {'ipaddress': res['fields'].get('ipaddress')}
            nodes[res['fields']['id']] = node
        return nodes

    def listResourceProviders(self, **kwargs):
        query = {'fields': ['id', 'cloudUnitType', 'images']}
        results = self._models.resourceprovider.search(query)['result']
        nodes = {}
        for res in results:
            node = {'cloudunittype': res['fields']['cloudUnitType']}
            node['images'] = res['fields']['images']
            nodes[res['fields']['id']] = node
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

    def registerVNC(self, url, **kwargs):
        vnc = self._models.vnc.new()
        vnc.url = url
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
        return info

    def storeInfo(self, data, timeout, **kwargs):
        """
        store info for period of time
        param:data store data for period of time
        param:timeout timeout for data
        result str
        """
        key = str(uuid.uuid4())
        self.cache.set(key, data, timeout)
        return key

    def listVNC(self, **kwargs):
        """
        list vnc urls
        result 
        """
        query = {'fields': ['url']}
        results = self._models.vnc.search(query)['result']
        return [res['fields']['url'] for res in results]

