from JumpScale import j

class libcloud_libvirt(j.code.classGetBase()):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="libvirt"
        self.appname="libcloud"
        #libcloud_libvirt_osis.__init__(self)


    def getFreeMacAddress(self, gid, **kwargs):
        """
        Get a free macaddres in this libvirt environment
        param:gid Grid id
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getFreeMacAddress")

    def getFreeNetworkId(self, gid, **kwargs):
        """
        Get a free NetworkId
        param:gid Grid id
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getFreeNetworkId")

    def listVNC(self, gid, **kwargs):
        """
        list vnc urls
        param:gid Grid id
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listVNC")

    def registerNetworkIdRange(self, gid, start, end, **kwargs):
        """
        Add a new network idrange
        param:gid Grid id
        param:start start of the range
        param:end end of the range
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerNetworkIdRange")

    def registerVNC(self, url, gid, **kwargs):
        """
        register a vnc application
        param:url url of the application
        param:gid register a vnc app linked to gid
        result int
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method registerVNC")

    def releaseNetworkId(self, gid, networkid, **kwargs):
        """
        Release a networkid.
        param:gid Grid id
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
