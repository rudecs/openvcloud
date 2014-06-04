[actor] @dbtype:mem,fs
    """
    iaas manager
    """    
    method:updateImages
        """     
        update IaaS Image
        """
        result:boolean

    method:setStackStatus
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available' 
        """
        var:statckid int,, id of the stack to update
        var:status str,, status e.g ENABLED, DISABLED, or HALTED.
        result: bool