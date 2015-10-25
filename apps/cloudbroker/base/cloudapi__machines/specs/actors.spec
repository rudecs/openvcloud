[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """

    method:create
        """
        Create a machine based on the available sizes, in a certain space.
        The user needs write access rights on the space.
        """
        var:cloudspaceId int,,id of space in which we want to create a machine
        var:name str,,name of machine
        var:description str,,optional description @tags: optional
        var:sizeId int,,id of the specific size
        var:imageId int,, id of the specific image
        var:disksize int,, size of base volume
        var:datadisks list,, list of extra data disks  @optional
        result:bool


    method:list
        """
        List the deployed machines in a space. Filtering based on status is possible.
        """
        var:cloudspaceId int,,id of space in which machine exists @tags: optional
        var:type str,,when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT) @tags: optional
        result:list

    method:get
        """
        Get information from a certain object.
        This contains all information about the machine.
        """
        var:machineId int,, id of machine
        result: bool

    method:delete
        """
        Delete a machine
        """
        var:machineId int,, id of the machine
        result: bool

    method:update
        """
        Change basic properties of a machine.
        Name, description can be changed with this action.
        """
        var:machineId int,, id of the machine
        var:name str,, name of the machine @tags: optional
        var:description str,, description of the machine @tags: optional
        var:size int,,size of the machine in CU @tags: optional

    method:start
        """
        start a machine.
        """
        var:machineId int,, id of the machine
        result:bool

    method:stop
        """
        stop a machine.
        """
        var:machineId int,, id of the machine
        result:bool

    method:reboot
        """
        reboot a machine.
        """
        var:machineId int,, id of the machine
        result:bool

    method:reset
        """
        Reset a machine, force reboot.
        """
        var:machineId int,, id of the machine
        result:bool

    method:pause
        """
        pause a machine.
        """
        var:machineId int,, id of the machine
        result:bool

    method:resume
        """
        resume a machine.
        """
        var:machineId int,, id of the machine
        result:bool

    method:addDisk
        """
        Add a disk to a machine
        """
        var:machineId int,,id of machine
        var:diskName str,,name of disk
        var:description str,,optional description
        var:size int,10,size in GByte
        var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
        result:int

    method:attachDisk
        """
        Attach a disk to a machine
        """
        var:machineId int,, id of machine
        var:diskId int,,id of disk to attach
        result:bool

    method:detachDisk
        """
        Detach a disk to a machine
        """
        var:machineId int,, id of machine
        var:diskId int,,id of disk to detach
        result:bool

    method:snapshot
        """
        """
        var:machineId int,,id of machine to snapshot
        var:name str,, Optional name to give snapshot
        result:int #returns id of new machine which gets created when snapshot was successfull

    method:listSnapshots
        """
        List the snapshot of a machine
        """
        var:machineId int,, id of the machine
        result:list


    method:deleteSnapshot
        """
        Delete a snapshot of a machine
        """
        var:machineId int,, id of the machine
        var:epoch str,, epoch time of snapshot
        result:str


    method:rollbackSnapshot
        """
        Rollback a snapshot of a machine
        """
        var:machineId int,, id of the machine
        var:epoch str,, epoch time of snapshot
        result:str

    method:createTemplate
        """
        Creates a template from the active machine
        """
        var:machineId int,, id of the machine
        var:templatename str,, name of the template
        var:basename str,, Snapshot id on which the template is based @tags: optional
        result:str


    method:importToNewMachine
        """
        restore export to a new machine
        """
        var:name str,,name of the new machine
        var:cloudspaceId int,, id of the cloudspace
        var:vmexportId int,, id of the export
        var:sizeId int,,id of the specific size
        var:description str,,optional description @tags: optional
        var:aws_access_key str,,s3 access key
        var:aws_secret_key str,,s3 secret key
        result:jobid


    method:export
        """
        Create a export/backup of a machine
        """
        var:machineId int,, id of the machine to backup
        var:name str,, Usefull name for this backup
        var:host str,, host to export(if s3)
        var:aws_access_key str,,s3 access key
        var:aws_secret_key str,,s3 secret key
        var:bucket str,,s3 bucket name
        result:jobid

    method:getConsoleUrl
        """
        get url to connect to console
        """
        var:machineId str,, id of machine to connect to console
        result:str #returns one time url used to connect ot console

    method:clone
        """
        clone machine
        """
        var:machineId str,,id of machine to clone
        var:name str,, name of cloned machine
        result:int #returns id of new machine cloned

    method:getHistory
        """
        Gets machine history
        """
        var:machineId str,,id of machine to clone
        var:size int,, result size
        result:list

    method:listExports
        """
        List exported images
        """
        var:machineId str,, id of the machine
        var:status str,, filter on specific status @tags: optional
        result:dict a json list

    method:addUser
        """
        Gives a user access to a vmachine
        """
        var:machineId int,, ID of a vmachine to share
        var:userId str,, ID of a user to share with
        var:accessType str,, 'R' for read only access, 'W' for Write access
        result:bool

    method:deleteUser
        """
        Revokes user's access to a vmachine
        """
        var:machineId int,, ID of a vmachine
        var:userId str,, ID of a user to revoke their access
        result:bool

    method:updateUser
        """
        Updates user's access rights to a vmachine
        """
        var:machineId int,, ID of a vmachine to share
        var:userId str,, ID of a user to share with
        var:accessType str,, 'R' for read only access, 'W' for Write access
        result:bool
        
    method:attachPublicNetwork
        """
        Revokes user's access to a vmachine
        """
        var:machineId int,, ID of a vmachine
        result:bool

    method:detachPublicNetwork
        """
        Revokes user's access to a vmachine
        """
        var:machineId int,, ID of a vmachine
        result:bool
