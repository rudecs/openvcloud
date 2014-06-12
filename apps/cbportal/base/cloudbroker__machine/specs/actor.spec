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

    method:export
        """
        Create a export/backup of a machine
        """
        var:machineId int,, id of the machine to backup
        var:name str,, Usefull name for this backup
        var:backuptype str,, Type e.g raw, condensed
        var:storage str,, Type of storage used. e.g S3 or RADOS.
        var:host str,, host to export(if s3) @tags: optional 
        var:aws_access_key str,,s3 access key @tags: optional 
        var:aws_secret_key str,,s3 secret key @tags: optional 
        result:jobid

    method:importbackup
        """
        Import a existing backup on a cpu node
        """
        var:vmexportId int,, id of the exportd to backup
        var:nid int,, node on which the bakcup is imported
        var:destinationpath str,, location where the backup should be located
        var:aws_access_key str,,s3 access key @tags: optional 
        var:aws_secret_key str,,s3 secret key @tags: optional 
        result:jobid


    method:listExports
        """
        List of created exports
        """
        result: list of created exports


