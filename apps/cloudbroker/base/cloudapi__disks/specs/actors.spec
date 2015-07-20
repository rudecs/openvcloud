[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """

    method:list
        """
        List the create disks machines in a space. Filtering based on status is possible.
        """
        var:accountId int,,id of accountId the disks belongs to
        var:type str,,type of the disks @tags: optional
        result:list

    method:get
        """
        Get information from a certain object.
        This contains all information about the machine.
        """
        var:diskId int,, id of disk
        result: disk

    method:delete
        """
        Delete a disk
        """
        var:diskId int,, id of the machine
        var:detach bool,,detach disk from machine first @optional
        result: bool

    method:create
        """
        Create a disk
        """
        var:accountId int,,id of the account
        var:gid int,,id of the grid
        var:name str,,name of disk
        var:description str,,optional description
        var:size int,10,size in GByte
        var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
        result:int
