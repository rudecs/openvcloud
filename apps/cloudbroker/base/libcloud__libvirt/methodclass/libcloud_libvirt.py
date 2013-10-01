from JumpScale import j
import JumpScale.grid.osis
from libcloud_libvirt_osis import libcloud_libvirt_osis
import ujson
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
        self.blobdb = self._getKeyValueStore()

    def _getKeyValueStore(self):
        print self.NAMESPACE
        print self.CATEGORY
        client = j.core.osis.getClient()
        if self.NAMESPACE not in client.listNamespaces():
            client.createNamespace(self.NAMESPACE, 'blob')
        if self.CATEGORY not in client.listNamespaceCategories(self.NAMESPACE):
           client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
        return j.core.osis.getClientForCategory(self.NAMESPACE, self.CATEGORY)


    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.libcloud.libvirt
        return self._cb
 

    def listImages(self, **kwargs):
        """
        List the available images
        result  
        """
        term = dict()
        query = {'fields': ['id', 'name', 'description', 'type', 'UNCPath', 'size']}
        results = self.cb.model_image_find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        return images

    

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result  
        
        """
        term = dict()
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
            ipaddresses = ujson.loads(self.blobdb.get('freeipaddresses'))
        except:
            #no list yet
            ipaddresses = []
            self.blobdb.set(key='freeipaddresses', value=ujson.dumps(ipaddresses))
        net = netaddr.IPNetwork(subnet)
        for i in net:
            ipaddresses.append(str(i))
        self.blobdb.set(key='freeipaddresses', value = ujson.dumps(ipaddresses))
        return True

    def getFreeIpaddress(self, **kwargs):
        """
        Get a free Ipaddress from one of ipadress ranges
        result  
        
        """
        ipaddresses = ujson.loads(self.blobdb.get('freeipaddresses'))
        if ipaddresses:
            ipaddress = ipaddresses.pop(0)
        else:
            ipaddress = None
        self.blobdb.set(key='freeipaddresses', value=ujson.dumps(ipaddresses))
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
            self.blobdb.set(key='lastmacaddress', value=int(newmacaddr))
            lastMac = int(newmacaddr)
        newmacaddr = lastMac + 1 
        macaddr = netaddr.EUI(newmacaddr)
        macaddr.dialect = netaddr.mac_unix 
        self.blobdb.set(key='lastmacaddress', value=newmacaddr)
        return str(macaddr)
    
    
    def releaseIpaddress(self, ipaddress, **kwargs):
        """
        Release a ipaddress.
        param:ipaddress string representing the ipaddres to release
        result bool 
        """
        ipaddresses = ujson.loads(self.blobdb.get('freeipaddresses'))
        ipaddresses.append(ipaddress)
        self.blobdb.set(key='freeipaddresses', value=ujson.dumps(ipaddresses))
        return True


    def registerNode(self, id, macaddress, **kwargs):
       """
       Register some basic node information E.g ipaddress
       param:id id of the node
       result str 
       
       """
       ipaddress = self.getFreeIpaddress()
       node = self.cb.models.node.new()
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
        term = dict()
        query = {'fields': ['id', 'ipaddress', 'macaddress']}
        results = self.cb.model_node_find(ujson.dumps(query))['result']
        nodes = {}
        for res in results:
            node = {'ipaddress': res['fields']['ipaddress']}
            nodes[res['fields']['id']] = node
        return nodes



    

