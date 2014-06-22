[actor] @dbtype:mem,osis
	"""
	API Actor api for managing account
	"""    
	method:create
		"""
		Create an extra account
		"""
		var:name str,,name of space to create
		var:access list,,list of ids of users which have full access to this space
		result:int  #returns id of space created

	method:delete
		"""
		Delete an account
		"""
		var:accountId int,, id of the account
		result:bool, True if deletion whas successfull

	method:list
		"""
		List accounts. 
		"""
		result:[], A json list, every element contains information of the list as a dictionary.

	method:update
	    """
	    Update an account name
        """
	    var:accountId int,, id of the account to change
	    var:name str,, name of the account
	    result:int # return id of account updated

	method:addUser
	    """
	    Give a user access rights.
	    Access rights can be 'R' or 'W'
	    """
	    var:accountId int,, id of the account
	    var:userId int,, id of the user to give access
	    var:accesstype str,, 'R' for read only access, 'W' for Write access
	    result:bool 

	method:deleteUser
		"""
		Delete a user from the account
		"""
	    var:accountId int,, id of the account
		var:userId int,, id of the user to remove
		result: bool

	method:get
		"""
		get account. 
		"""
        var:accountId int,, id of the account
		result:dict A json dict


	method:listTemplates
		"""
		List templates which can be managed by this account
		"""
        var:accountId int,, id of the account
		result:dict A json dict

	method:getCreditBalance
		"""
		Get the current available credit
		"""
		result:dict A json dict containing the available credit
		
	method:getCreditHistory
		"""
		Get all the credit transactions (positive and negative) for this account.
		"""
		var:accountId int,, id of the account
		result:[], A json list with the transactions details.
