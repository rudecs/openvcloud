[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """

    method:list
        """
        List the created disks belonging to an account
        """
        var:accountId int,,id of accountId the disks belongs to
        var:type str,,type of the disks @tags: optional
        result:list, list with every element containing details of a disk as a dict

    method:get
        """
        Get disk details
        """
        var:diskId int,, id of the disk
        result:dict, dict with the disk details


    method:limitIO
        """
        Get disk details
        """
        var:diskId int,, id of the disk
        var:iops int,, IO per second to limit the disk to
        result:dict, dict with the disk details

    method:delete
        """
        Delete a disk
        """
        var:diskId int,, id of disk to delete
        var:detach bool,,detach disk from machine first @optional
        result: bool, True if disk was deleted successfully

    method:create
        """
        Create a disk
        """
        var:accountId int,,id of the account
        var:gid int,,id of the grid
        var:name str,,name of disk
        var:description str,,description of disk
        var:size int,10,size in GBytes, default is 0
        var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
        result:int, the id of the created disk
