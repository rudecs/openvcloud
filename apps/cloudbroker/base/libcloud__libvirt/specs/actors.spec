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


