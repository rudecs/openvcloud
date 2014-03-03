from JumpScale import j

class libcloud_libvirt(j.code.classGetBase()):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="libvirt"
        self.appname="libcloud"
        #libcloud_libvirt_osis.__init__(self)
    

        pass

    def addFreeSubnet(self, subnet, networkid, **kwargs):
        """
        Add a free subnet to the range
        param:subnet subnet in CIDR notation
        param:networkid id of the network
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addFreeSubnet")
    

    def getFreeIpaddress(self, networkid, **kwargs):
        """
        Get a free Ipaddress from one of ipadress ranges
        param:networkid id representing the network
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getFreeIpaddress")
    

    def getFreeMacAddress(self, **kwargs):
        """
        Get a free macaddres in this libvirt environment
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getFreeMacAddress")
    

    def getFreeNetworkId(self, **kwargs):
        """
        Get a free NetworkId
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getFreeNetworkId")
    

    def getNode(self, id, **kwargs):
        """
        Get a node
        param:id id of the node
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getNode")
    

    def linkImage(self, imageid, resourceprovider, **kwargs):
        """
        Link a image to a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method linkImage")
    

    def listImages(self, resourceid, **kwargs):
        """
        List the available images.
        If no resourceid is provided, all the images are listed.
        resourceid is the id of the resourceprovider and is a md5sum of the uri. md5.new(uri).hexdigest()
        param:resourceid optional resourceproviderid.
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listImages")
    

    def listNodes(self, **kwargs):
        """
        List all nodes
        result list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listNodes")
    

    def listResourceProviders(self, **kwargs):
        """
        List all registered resource providers
        result list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listResourceProviders")
    

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listSizes")
    

    def listVNC(self, **kwargs):
        """
        list vnc urls
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listVNC")
    

    def registerNetworkIdRange(self, start, end, **kwargs):
        """
        Add a new network idrange
        param:start start of the range
        param:end end of the range
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerNetworkIdRange")
    

    def registerNode(self, id, macaddress, networkid, **kwargs):
        """
        Register some basic node information E.g ipaddress
        param:id id of the node
        param:macaddress macaddress of the node
        param:networkid id of the network
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerNode")
    

    def registerVNC(self, url, **kwargs):
        """
        register a vnc application
        param:url url of the application
        result int
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerVNC")
    

    def releaseIpaddress(self, networkid, ipaddress, **kwargs):
        """
        Release a ipaddress.
        param:networkid id representing the network
        param:ipaddress string representing the ipaddres to release
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method releaseIpaddress")
    

    def releaseNetworkId(self, networkid, **kwargs):
        """
        Release a networkid.
        param:networkid int representing the netowrkid to release
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method releaseNetworkId")
    

    def retreiveInfo(self, key, reset, **kwargs):
        """
        get info
        param:key key of data
        param:reset reset info
        result dict
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method retreiveInfo")
    

    def storeInfo(self, data, timeout, **kwargs):
        """
        store info for period of time
        param:data store data for period of time
        param:timeout timeout for data
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method storeInfo")
    

    def unLinkImage(self, imageid, resourceprovider, **kwargs):
        """
        Unlink a image from a resource provider
        param:imageid unique id of the image
        param:resourceprovider unique id of the resourceprovider
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method unLinkImage")
    

    def unregisterNode(self, id, **kwargs):
        """
        Unregister a node.
        param:id id of the node to unregister
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method unregisterNode")
    
