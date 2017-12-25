[actor] @dbtype:mem,osis
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    """
    method: getFreeMacAddress
        """
        Get a free macaddres in this libvirt environment
        """
        var:gid int,, Grid id
        result: free macaddress in the unix mac address format

    method: getFreeNetworkId
    """
    Get a free NetworkId
    """
        var:gid int,, Grid id
        result: free ipaddress composed as int

    method: releaseNetworkId
    """
    Release a networkid.
    """
        var:gid int,, Grid id
        var:networkid id,,int representing the netowrkid to release
        result:bool


    method: registerNetworkIdRange
    """
    Add a new network idrange
    """
        var:gid int,, Grid id
        var:start int,,start of the range
        var:end int,,end of the range
        result: bool


    method: registerVNC
    """
    register a vnc application
    """
        var:url str,, url of the application
        var:gid int,, register a vnc app linked to gid
        result:int

    method: listVNC
    """
    list vnc urls
    """
        var:gid int,, Grid id
        result: list

    method: storeInfo
    """
    store info for period of time
    """
        var:data dict,, store data for period of time
        var:timeout int,, timeout for data
        result:str key where data is stored

    method: retreiveInfo
    """
    get info
    """
        var:key str,, key of data
        var:reset bool,, reset info
        result:dict if key valid otherwise None
