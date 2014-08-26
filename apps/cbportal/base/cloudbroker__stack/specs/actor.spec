[actor] @dbtype:mem,fs
    """
    stack manager
    """    
    method:enable
        """     
        enable a stack
        """
        var:stackId int,,stack id
        var:message str,,message. Must be less than 30 characters


    method:disable
        """     
        enable a stack
        """
        var:stackId int,,stack id
        var:message str,,message. Must be less than 30 characters
