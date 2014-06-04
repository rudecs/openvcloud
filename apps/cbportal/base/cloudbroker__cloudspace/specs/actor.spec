[actor] @dbtype:mem,fs
    """
    finance manager
    """    
    method:destroy
        """     
        destroy cloudspace
        """
        var:accountname str,,name of account
        var:cloudspaceName str,,name of cloudspace
        var:cloudspaceId str,,ID of cloudspace
        var:reason str,, reason for destroying the cloudspace