[actor] @dbtype:mem,osis
	"""
	API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces
	"""    
	method:create
		"""
		Create a extra cloudspace
		"""
        var:accountId str,, Id of acount this cloudspace belongs to
		var:name str,,name of space to create
		var:access str,,id of the user which has full access to the space
		var:maxMemoryCapacity int,,max size of memory in space (in GB) @tags: optional 
		var:maxDiskCapacity int,,max size of aggregated disks (in GB) @tags: optional 
		result:int  #returns id of space created

	method:deploy
		"""
	    Create VFW for cloudspace	
		"""
		var:cloudspaceId int,, id of the cloudspace
		result:str Status of deployment 

	method:delete
		"""
		Delete a cloudspace.
		"""
		var:cloudspaceId int,, id of the cloudspace
		result:bool, True if deletion whas successfull

	method:list
		"""
		List cloudspaces. 
		"""
		result:[], A json list, every element contains information of the list as a dictionary.

	method:get
		"""
		get cloudspaces. 
		"""
        var:cloudspaceId int,, id of the cloudspace
		result:dict A json dict

	method:update
	    """
	    Update a cloudspace name and capacity parameters can be updated
	    """
	    var:cloudspaceId int,, id of the cloudspace to change
	    var:name str,, name of the cloudspace
	    var:maxMemoryCapacity int,, max size of memory in space(in GB)
	    var:maxDiskCapacity int,, max size of aggregated disks(in GB)
	    result:int # return id of space updated

	method:addUser
	    """
	    Give a user access rights.
	    Access rights can be 'R' or 'W'
	    """
	    var:cloudspaceId int,, id of the cloudspace
	    var:userId int,, id of the user to give access
	    var:accesstype str,, 'R' for read only access, 'W' for Write access
	    result:bool 

	method:deleteUser
		"""
		Delete a user from the cloudspace
		"""
	    var:cloudspaceId int,, id of the cloudspace
		var:userId int,, id of the user to remove
		result: bool

    method:getDefenseShield
        """
        Get information about the defense sheild
        """
        var:cloudspaceId int,, id of the cloudspace
        result: object
