[actor] @dbtype:mem,osis
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    """
    method: listSizes
	"""
	List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        """
        result: list of sizes contains id, memory, cpu , disksize for every size

    method: listImages
	"""
    List the available images.
    If no resourceid is provided, all the images are listed.
    resourceid is the id of the resourceprovider and is a md5sum of the uri. md5.new(uri).hexdigest()
	"""
        var:resourceid str,, optional resourceproviderid. @tags: optional
        result: list of images supported by the stack(e.g libvirt)


    method: getFreeMacAddress
        """
        Get a free macaddres in this libvirt environment
        """
        var:gid int,, Grid id
        result: free macaddress in the unix mac address format

    #method: getFreeIpaddress
    #"""
    #Get a free Ipaddress from one of ipadress ranges
    #"""
    #    var:networkid int,, id representing the network
    #    result: free ipaddress composed as string

    method: releaseIpaddress
    """
    Release a ipaddress.
    """
        var:networkid int,, id representing the network
        var:ipaddress str,,string representing the ipaddres to release
        result:bool

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


    #method: addFreeSubnet
    #"""
    #Add a free subnet to the range
    #"""
    #    var:subnet str,,subnet in CIDR notation
    #    var:networkid int,,id of the network
    #    result:bool

    method: registerNetworkIdRange
    """
    Add a new network idrange
    """
        var:gid int,, Grid id
        var:start int,,start of the range
        var:end int,,end of the range
        result: bool

    method: registerNode
    """
    Register some basic node information E.g ipaddress
    """
        var:id str,,id of the node
        var:macaddress str,,macaddress of the node
        var:networkid str,, id of the network
        result:str


    method: registerImage
    """
    Register image in model
    """
        var:name str,,name of the image
        var:category str,,catergory of the image
        var:imageid str,, id of the image
        var:size int,,size of the image
        var:gid int,,grid id
        result:str


    method: removeImage
    """
    remove image from model
    """
        var:imageid str,,id of the image
        var:gid int,,grid id
        result:str

    method: getNode
    """
    Get a node
    """
        var:id str,,id of the node
        result:str

    method: unregisterNode
    """
    Unregister a node.
    """
        var:id str,,id of the node to unregister
        result:bool


    method: listNodes
    """
    List all nodes
    """
        result:list of node information, sorted by id

    method: listResourceProviders
    """
    List all registered resource providers
    """
        var:gid int,, Grid id
        result:list of all registered resource providers

    method: linkImage
    """
    Link a image to a resource provider
    """
        var:imageid str,, unique id of the image
        var:resourceprovider str,, unique id of the resourceprovider
        result:bool

    method: unLinkImage
    """
    Unlink a image from a resource provider
    """
        var:imageid str,, unique id of the image
        var:resourceprovider str,, unique id of the resourceprovider
        result:bool


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
