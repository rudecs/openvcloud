[actor] @dbtype:mem,fs
    """
    machine manager
    """
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

    method:destroy
        """
        Destroys a machine
        """
        var:accountName str,,Account name
        var:spaceName str,,Space name
        var:machineId int,,Machine id
        var:reason str,,Reason

    method:tag
        """
        Adds a tag to a machine, useful for indexing and following a (set of) machines
        """
        var:machineId int,, id of the machine to tag
        var:tagname str,, tag

    method:untag
        """
        Removes a specific tag from a machine
        """
        var:machineId int,, id of the machine to untag
        var:tagname str,, tag

    method:list
        """
        List the undestroyed machines based on specific criteria
        At least one of the criteria needs to be passed
        """
        var:tag str,, a specific tag @optional
        var:computenode str,, name of a specific computenode
        var:accountname str,, specific account
        var:cloudspaceId int,, specific cloudspace
