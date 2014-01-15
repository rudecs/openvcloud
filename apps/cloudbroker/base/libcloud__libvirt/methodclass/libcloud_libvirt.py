from JumpScale import j
import JumpScale.grid.osis
from libcloud_libvirt_osis import libcloud_libvirt_osis
import uuid
ujson = j.db.serializers.ujson
import memcache
import netaddr
class libcloud_libvirt(libcloud_libvirt_osis):
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
        libcloud_libvirt_osis.__init__(self)
        self._cb = None
        self.cache = memcache.Client(['localhost:11211'])
        self.blobdb = self._getKeyValueStore()

    def _getKeyValueStore(self):
        print self.NAMESPACE
        print self.CATEGORY
        client = j.core.osis.getClient(user='root')
        if self.NAMESPACE not in client.listNamespaces():
            client.createNamespace(self.NAMESPACE, template='blob')
        if self.CATEGORY not in client.listNamespaceCategories(self.NAMESPACE):
           client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
        return j.core.osis.getClientForCategory(client, self.NAMESPACE, self.CATEGORY)


    @property
    def cb(self):
        if not self._cb:
            self._cb = modelactions(self.models)
        return self._cb
 
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
                rp = self.cb.model_resourceprovider_get(resourceid)
            except:
                return []
            for i in rp['images']:
                images.append(self.cb.model_image_get(i))
            return images
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
        results = self.cb.model_size_find(ujson.dumps(query))['result']
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
       self.cb.model_node_set(node)
       return ipaddress

    def unregisterNode(self, id, **kwargs):
        """
        Unregister a node.
        param:id id of the node to unregister
        result bool

        """
        node = self.cb.model_node_get(id)
        self.releaseIpaddress(node['ipaddress'])
        self.cb.model_node_delete(id)
        return True

    def listNodes(self, **kwargs):
        """
        List all nodes
        result

        """
        query = {'fields': ['id', 'ipaddress', 'macaddress']}
        results = self.cb.model_node_find(ujson.dumps(query))['result']
        nodes = {}
        for res in results:
            node = {'ipaddress': res['fields'].get('ipaddress')}
            nodes[res['fields']['id']] = node
        return nodes

    def listResourceProviders(self, **kwargs):
        query = {'fields': ['id', 'cloudUnitType', 'images']}
        results = self.cb.model_resourceprovider_find(ujson.dumps(query))['result']
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
        res = self.cb.model_resourceprovider_get(resourceprovider)
        try:
            res['images'].remove(imageid)
        except ValueError:
            pass
        self.cb.model_resourceprovider_set(res)
        return True

    def linkImage(self, imageid, resourceprovider, **kwargs):
        """
        Link a image to a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool

        """
        res = self.cb.model_resourceprovider_get(resourceprovider)
        if not res['images']:
            res['images'] = []
        res['images'].append(imageid)
        print res
        self.cb.model_resourceprovider_set(res)
        return True

    def registerVNC(self, url, **kwargs):
        vnc = self.models.vnc.new()
        vnc.url = url
        return self.cb.model_vnc_set(vnc)

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
        results = self.cb.model_vnc_find(ujson.dumps(query))['result']
        return [res['fields']['url'] for res in results]


class modelactions():
 
    def __init__(self, models):
        self.models = models

    def model_image_create(self, id, name, description, UNCPath, size, type, **kwargs):
        """
        Create a new model
        param:id unique id of the image
        param:name name of the image
        param:description extra description of the image
        param:UNCPath location of the image (uncpath like used in pylabs); includes the login/passwd info
        param:size size in MByte
        param:type dot separated list of independant terms known terms are: tar;gz;sso e.g. sso dump inn tar.gz format would be sso.tar.gz  (always in lcas)
        result json 
        
        """
        
        image = self.models.image.new()
        image.id = id
        image.name = name
        image.description = description
        image.UNCPath = UNCPath
        image.size = size
        image.type = type
        
        return self.models.image.set(image)
                
    

    def model_image_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.image.datatables() #@todo
                    
    

    def model_image_delete(self, id, guid='', **kwargs):
        """
        remove the model image with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.image.delete(guid=guid, id=id)
                    
    

    def model_image_find(self, query='', **kwargs):
        """
        query to model image
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.image.find(query)            
                    
    

    def model_image_get(self, id, guid='', **kwargs):
        """
        get model image with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.image.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_image_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.image.list()            
                    
    

    def model_image_new(self, **kwargs):
        """
        Create a new modelobjectimage instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.image.new()
                    
    

    def model_image_set(self, data='', **kwargs):
        """
        Saves model image instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.image.set(data)            
                    
    

    def model_node_create(self, id, ipaddress, macaddress, **kwargs):
        """
        Create a new model
        param:id id of the node
        param:ipaddress ipaddress of the node
        param:macaddress macaddress of the node
        result json 
        
        """
        
        node = self.models.node.new()
        node.id = id
        node.ipaddress = ipaddress
        node.macaddress = macaddress
        
        return self.models.node.set(node)
                
    

    def model_node_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.node.datatables() #@todo
                    
    

    def model_node_delete(self, id, guid='', **kwargs):
        """
        remove the model node with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.node.delete(guid=guid, id=id)
                    
    

    def model_node_find(self, query='', **kwargs):
        """
        query to model node
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.node.find(query)            
                    
    

    def model_node_get(self, id, guid='', **kwargs):
        """
        get model node with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.node.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_node_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.node.list()            
                    
    

    def model_node_new(self, **kwargs):
        """
        Create a new modelobjectnode instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.node.new()
                    
    

    def model_node_set(self, data='', **kwargs):
        """
        Saves model node instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.node.set(data)            
                    
    

    def model_resourceprovider_create(self, id, cloudUnitType, images, **kwargs):
        """
        Create a new model
        param:id resourceprovider id is the uri of the compute node
        param:cloudUnitType (CU,VSU,SU,NU)
        param:images list of images ids supported by this resource
        result json 
        
        """
        
        resourceprovider = self.models.resourceprovider.new()
        resourceprovider.id = id
        resourceprovider.cloudUnitType = cloudUnitType
        resourceprovider.images = images
        
        return self.models.resourceprovider.set(resourceprovider)
                
    

    def model_resourceprovider_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.resourceprovider.datatables() #@todo
                    
    

    def model_resourceprovider_delete(self, id, guid='', **kwargs):
        """
        remove the model resourceprovider with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.resourceprovider.delete(guid=guid, id=id)
                    
    

    def model_resourceprovider_find(self, query='', **kwargs):
        """
        query to model resourceprovider
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.resourceprovider.find(query)            
                    
    

    def model_resourceprovider_get(self, id, guid='', **kwargs):
        """
        get model resourceprovider with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.resourceprovider.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_resourceprovider_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.resourceprovider.list()            
                    
    

    def model_resourceprovider_new(self, **kwargs):
        """
        Create a new modelobjectresourceprovider instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.resourceprovider.new()
                    
    

    def model_resourceprovider_set(self, data='', **kwargs):
        """
        Saves model resourceprovider instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.resourceprovider.set(data)            
                    
    

    def model_size_create(self, name, memory, vcpus, disk, **kwargs):
        """
        Create a new model
        param:name Public name of the size
        param:memory Memory in Mb
        param:vcpus Number of virtual cpus assigned to the machine
        param:disk disk size in GB
        result json 
        
        """
        
        size = self.models.size.new()
        size.name = name
        size.memory = memory
        size.vcpus = vcpus
        size.disk = disk
        
        return self.models.size.set(size)
                
    

    def model_size_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.size.datatables() #@todo
                    
    

    def model_size_delete(self, id, guid='', **kwargs):
        """
        remove the model size with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.size.delete(guid=guid, id=id)
                    
    

    def model_size_find(self, query='', **kwargs):
        """
        query to model size
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.size.find(query)            
                    
    

    def model_size_get(self, id, guid='', **kwargs):
        """
        get model size with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.size.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_size_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.size.list()            
                    
    

    def model_size_new(self, **kwargs):
        """
        Create a new modelobjectsize instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.size.new()
                    
    

    def model_size_set(self, data='', **kwargs):
        """
        Saves model size instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.size.set(data)            
                    
    

    def model_vnc_create(self, url, **kwargs):
        """
        Create a new model
        param:url Url of vnc proxy
        result json 
        
        """
        
        vnc = self.models.vnc.new()
        vnc.url = url
        
        return self.models.vnc.set(vnc)
                
    

    def model_vnc_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.vnc.datatables() #@todo
                    
    

    def model_vnc_delete(self, id, guid='', **kwargs):
        """
        remove the model vnc with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.vnc.delete(guid=guid, id=id)
                    
    

    def model_vnc_find(self, query='', **kwargs):
        """
        query to model vnc
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.vnc.find(query)            
                    
    

    def model_vnc_get(self, id, guid='', **kwargs):
        """
        get model vnc with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.vnc.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_vnc_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.vnc.list()            
                    
    

    def model_vnc_new(self, **kwargs):
        """
        Create a new modelobjectvnc instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.vnc.new()
                    
    

    def model_vnc_set(self, data='', **kwargs):
        """
        Saves model vnc instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.vnc.set(data)     
