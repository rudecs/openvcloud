[actor] @dbtype:mem,fs
    """
    Operator actions for interventions specific to a user
    """
    method:generateAuthorizationKey
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        """
        var:username str,,name of the user an authorization key is required for

    method:updatePassword
        """
        Update user's password
        """
        var:username str,, id of user to reset password for
        var:password str,, new password
        result:bool

    method:sendResetPasswordLink
        """
        send reset password of user to their email address
        """
        var:username str,, id of user
        result:bool

    method:delete
       """
       Delete a user 
       """
       var:username str,, id of user
       result:bool
