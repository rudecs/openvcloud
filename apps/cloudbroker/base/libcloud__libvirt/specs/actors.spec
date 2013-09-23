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
        List the available images
	"""
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
        result: list of node information, sorted by id




