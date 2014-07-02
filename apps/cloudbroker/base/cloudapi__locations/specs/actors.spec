[actor] @dbtype:mem,osis
	"""
	API Actor api for managing locations
    """    

	method:list @noauth
		"""
		List locations. 
		"""
		result:[], A json list, every element contains information of the list as a dictionary.

