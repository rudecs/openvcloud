from JumpScale import j
from libcloud_libvirt_osis import libcloud_libvirt_osis


class libcloud_libvirt(libcloud_libvirt_osis):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="libvirt"
        self.appname="libcloud"
        libcloud_libvirt_osis.__init__(self)
    

        pass

    def addFreeSubnet(self, subnet, **kwargs):
        """
        Add a free subnet to the range
        param:subnet subnet in CIDR notation
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addFreeSubnet")
    

    def getFreeIpaddress(self, **kwargs):
        """
        Get a free Ipaddress from one of ipadress ranges
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
    

    def listImages(self, **kwargs):
        """
        List the available images
        result  
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listImages")
    

    def listNodes(self, **kwargs):
        """
        List all nodes
        result  
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listNodes")
    

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result  
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listSizes")
    

    def registerNode(self, id, macaddress, **kwargs):
        """
        Register some basic node information E.g ipaddress
        param:id id of the node
        param:macaddress macaddress of the node
        result str 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerNode")
    

    def releaseIpaddress(self, ipaddress, **kwargs):
        """
        Release a ipaddress.
        param:ipaddress string representing the ipaddres to release
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method releaseIpaddress")
    

    def unregisterNode(self, id, **kwargs):
        """
        Unregister a node.
        param:id id of the node to unregister
        result bool 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method unregisterNode")
    
