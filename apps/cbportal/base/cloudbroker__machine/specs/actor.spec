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

    method:moveToDifferentComputeNode
        """
        Live-migrates a machine to a different CPU node.
        If no targetnode is given, the normal capacity scheduling is used to determine a targetnode
        """
        var:accountName str,,Account name
        var:machineId int,,Machine id
        var:targetComputeNode str,, Name of the compute node the machine has to be moved to @optional
        var:withSnapshots bool,, Defaults to true @optional
        var:collapseSnapshots bool,, Sanitize snapshots, defaults to false @optional
    
    method:export
        """
        Create a export/backup of a machine
        """
        var:machineId int,, id of the machine to backup
        var:name str,, Usefull name for this backup
        var:backuptype str,, Type e.g raw, condensed
        var:storage str,, Type of storage used. e.g S3 or RADOS.
        var:bucketname str,,bucket name 
        var:host str,, host to export(if s3) @tags: optional
        var:aws_access_key str,,s3 access key @tags: optional 
        var:aws_secret_key str,,s3 secret key @tags: optional
        var:bucketname str,,bucket name 
        result:jobid

    method:tag
        """
        Adds a tag to a machine, useful for indexing and following a (set of) machines
        """
        var:machineId int,, id of the machine to tag
        var:tagName str,, tag
       
    method:restore
        """
        Import a existing backup on a cpu node
        """
        var:vmexportId int,, id of the exportd to backup
        var:nid int,, node on which the bakcup is imported
        var:destinationpath str,, location where the backup should be located
        var:aws_access_key str,,s3 access key @tags: optional 
        var:aws_secret_key str,,s3 secret key @tags: optional 
        result:jobid

    method:untag
        """
        Removes a specific tag from a machine
        """
        var:machineId int,, id of the machine to untag
        var:tagName str,, tag

    method:listExports
        """
        List of created exports
        """
        var:status str,,status of the backup @tags: optional
        var:machineId int,,id of the machine @tags: optional
        result: list of created exports 
    
    method:list
        """
        List the undestroyed machines based on specific criteria
        At least one of the criteria needs to be passed
        """
        var:tag str,, a specific tag @optional
        var:computeNode str,, name of a specific computenode @optional
        var:accountName str,, specific account @optional
        var:cloudspaceId int,, specific cloudspace @optional
    
    method:checkImageChain
        """
        Checks on the computenode the vm is on if the vm image is there
        Check the chain of the vmimage to see if parents are there (the template starting from)
        (executes the vm.hdcheck jumpscript)
        """
        var:machineId int,, id of the machine
        result:dict,, location of all files & their size
