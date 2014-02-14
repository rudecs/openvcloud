from JumpScale import j
import JumpScale.grid.osis
import uuid
ujson = j.db.serializers.ujson
import memcache
import netaddr

class Models(object):
    def __init__(self, client, namespace):
        for category in client.listNamespaceCategories(namespace):
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
        self.actorname="libvirt"
        self.appname="libcloud"
        self._client = j.core.osis.getClient(user='root')
        self.cache = memcache.Client(['localhost:11211'])
        self.blobdb = self._getKeyValueStore()
        self.models = Models(self._client, self.actorname)

    def _getKeyValueStore(self):
        print self.NAMESPACE
        print self.CATEGORY
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
                rp = self.models.resourceprovider.get(resourceid)
            except:
                return []
            for i in rp.images:
                images.append(self.image.get(i).__dict__)
            return images.__dict__
        query = {'fields': ['id', 'name', 'description', 'type', 'UNCPath', 'size', 'extra']}
        results = self.cb.model_image_find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        return images

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result
        """
        query = {'fields': ['id', 'name', 'vcpus', 'memory', 'disk']}
        results = self.models.size.search(query)['result']
        sizes = [res['fields'] for res in results]
        return sizes

    def addFreeSubnet(self, subnet, **kwargs):
        """
        Add a free subnet to the range
        param:subnet subnet in CIDR notation e.g network/subnetmask
        result bool
        """
        try:
            ipaddresses = self.blobdb.get('freeipaddresses')
        except:
            #no list yet
            ipaddresses = []
            self.blobdb.set(key='freeipaddresses', obj=ujson.dumps(ipaddresses))
        net = netaddr.IPNetwork(subnet)
        netrange = net[2:-2]
        for i in netrange:
            if i != net.broadcast:
                ipaddresses.append(str(i))
        self.blobdb.set(key='freeipaddresses', obj=ujson.dumps(ipaddresses))
        return True

    def getFreeIpaddress(self, **kwargs):
        """
        Get a free Ipaddress from one of ipadress ranges
        result
        """
        ipaddresses = self.blobdb.get('freeipaddresses')
        if ipaddresses:
            ipaddress = ipaddresses.pop(0)
        else:
            ipaddress = None
        self.blobdb.set(key='freeipaddresses', obj=ujson.dumps(ipaddresses))
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

    def releaseIpaddress(self, ipaddress, **kwargs):
        """
        Release a ipaddress.
        param:ipaddress string representing the ipaddres to release
        result bool
        """
        ipaddresses = self.blobdb.get('freeipaddresses')
        ipaddresses.append(ipaddress)
        self.blobdb.set(key='freeipaddresses', obj=ujson.dumps(ipaddresses))
        return True

    def registerNode(self, id, macaddress, **kwargs):
       """
       Register some basic node information E.g ipaddress
       param:id id of the node
       result str
       """
       ipaddress = self.getFreeIpaddress()
       node = self.models.node.new()
       node.id = id
       node.ipaddress = ipaddress
       node.macaddress = macaddress
       self.modles.node.set(node)
       return ipaddress

    def unregisterNode(self, id, **kwargs):
        """
        Unregister a node.
        param:id id of the node to unregister
        result bool
        """
        node = self.models.node.get(id)
        self.releaseIpaddress(node.ipaddress)
        self.models.node.delete(id)
        return True

    def listNodes(self, **kwargs):
        """
        List all nodes
        result

        """
        query = {'fields': ['id', 'ipaddress', 'macaddress']}
        results = self.models.node.search(query)['result']
        nodes = {}
        for res in results:
            node = {'ipaddress': res['fields'].get('ipaddress')}
            nodes[res['fields']['id']] = node
        return nodes

    def listResourceProviders(self, **kwargs):
        query = {'fields': ['id', 'cloudUnitType', 'images']}
        results = self.modles.resourceprovider.search(query)['result']
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
        res = self.modles.resourceprovider.get(resourceprovider)
        try:
            res.images.remove(imageid)
        except ValueError:
            pass
        self.models.resourceprovider.set(res)
        return True

    def linkImage(self, imageid, resourceprovider, **kwargs):
        """
        Link a image to a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool
        """
        res = self.modles.resourceprovider.get(resourceprovider)
        if not res.images:
            res.images = []
        res.images.append(imageid)
        print res
        self.models.resourceprovider.set(res)
        return True

    def registerVNC(self, url, **kwargs):
        vnc = self.models.vnc.new()
        vnc.url = url
        return self.models.vnc.set(vnc)

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
        results = self.modles.vnc.search(query)['result']
        return [res['fields']['url'] for res in results]

