[actor] @dbtype:mem,osis
	"""
	User management
	"""

    method:authenticate @noauth
	    """
	    The function evaluates the provided username and password and returns a session key.
	    The session key can be used for doing api requests. E.g this is the authkey parameter in every actor request.
	    A session key is only vallid for a limited time.
	    """

	    var:username str,,username to validate
	    var:password str,,password to validate
	    result:str,,session key.

	method:get
	    """
	    Get information of a existing username based on username id
	    """
        var:username str,,username of the user
        result:dict,,user information.

	method:setData
	    """
	    Set extra user information
	    """
        var:data str,,data to set to user in json format
        result:True

    method:getMatchingUsernames
        """
        Get a list of the matching usernames for a given string
        """
        var:usernameregex str,,regex of the usernames to searched for
        var:limit int,5,the number of usernames to return
        result:list,,list of dicts with the username and url of the gravatar of the user

    method:isValidInviteUserToken @noauth
        """
        Check if the inviteusertoken and emailaddress pair are valid and matching
        """
        var:inviteusertoken str,,the token that was previously sent to the invited user email
        var:emailaddress str,,email address for the user
        result:bool