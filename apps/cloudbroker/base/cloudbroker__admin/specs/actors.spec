[actor] @dbtype:mem,osis
    """
    Admin interface to manage the cloudbroker
    """

    method:setStackStatus
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available' 
        """
        var:statckid int,, id of the stack to update
        var:status str,, status e.g ENABLED, DISABLED, or HALTED.
        result: bool


    method:createOnStack
        """
        Create a machine on a specific stackid
        """
        var:cloudspaceId int,,id of space in which we want to create a machine
        var:name str,,name of machine
        var:description str,,optional description @tags: optional 
        var:sizeId int,,id of the specific size
        var:imageId int,, id of the specific image
        var:disksize int,, size of base volume
        var:stackid int,, id of the stack
        result:bool   

