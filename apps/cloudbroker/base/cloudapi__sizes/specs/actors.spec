[actor] @dbtype:mem,osis
	"""
	Lists all the configured flavors available.
	A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).
	"""    

	method:list
		"""
		List the availabe flavors, filtering can be based on the user which is doing the request
		"""
		var:cloudspaceId int,, id of the space
		result:list of flavors contains id CU and disksize for every flavor.