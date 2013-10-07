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
        result: free macaddress in the unix mac address format

    method: getFreeIpaddress
    """
    Get a free Ipaddress from one of ipadress ranges
    """
        result: free ipaddress composed as string

    method: releaseIpaddress
    """
    Release a ipaddress.
    """
        var:ipaddress str,,string representing the ipaddres to release
        result:bool

    method: addFreeSubnet
    """
    Add a free subnet to the range
    """
        var:subnet str,,subnet in CIDR notation
        result:bool

    method: registerNode
    """
    Register some basic node information E.g ipaddress 
    """ 
        var:id str,,id of the node
        var:macaddress str,,macaddress of the node
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




