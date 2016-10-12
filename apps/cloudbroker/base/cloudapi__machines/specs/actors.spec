[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources
    """

    method:create
        """
        Create a machine based on the available sizes, in a certain cloud space
        The user needs write access rights on the cloud space
        """
        var:cloudspaceId int,,id of cloud space in which we want to create a machine
        var:name str,,name of machine @tags validator:name
        var:description str,,optional description @tags: optional
        var:sizeId int,,id of the specific size
        var:imageId int,, id of the specific image
        var:disksize int,, size of base volume
        var:datadisks list(int),, list of extra data disks in gigabytes  @optional
        result:bool


    method:list
        """
        List the deployed machines in a space. Filtering based on status is possible
        """
        var:cloudspaceId int,,id of cloud space in which machine exists @tags: optional
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
        Change basic properties of a machine
        Name, description can be changed with this action.
        """
        var:machineId int,, id of the machine
        var:name str,, name of the machine @tags: optional validator:name
        var:description str,, description of the machine @tags: optional

    method:start
        """
        Start the machine
        """
        var:machineId int,, id of the machine
        result:bool

    method:stop
        """
        Stop the machine
        """
        var:machineId int,, id of the machine
        result:bool

    method:reboot
        """
        Reboot the machine
        """
        var:machineId int,, id of the machine
        result:bool

    method:reset
        """
        Reset the machine, force reboot
        """
        var:machineId int,, id of the machine
        result:bool

    method:pause
        """
        Pause the machine
        """
        var:machineId int,, id of the machine
        result:bool

    method:resume
        """
        Resume the machine
        """
        var:machineId int,, id of the machine
        result:bool

    method:addDisk
        """
        Create and attach a disk to the machine
        """
        var:machineId int,,id of the machine
        var:diskName str,,name of disk
        var:description str,,optional description
        var:size int,10,size in GByte
        var:type str,B, (B;D;T) B=Boot;D=Data;T=Temp
        result:int, id of the disk

    method:attachDisk
        """
        Attach a disk to the machine
        """
        var:machineId int,, id of the machine
        var:diskId int,,id of disk to attach
        result:bool, True if disk was attached successfully

    method:detachDisk
        """
        Detach a disk from the machine
        """
        var:machineId int,, id of the machine
        var:diskId int,,id of disk to detach
        result:bool, True if disk was detached successfully

    method:snapshot
        """
        Take a snapshot of the machine
        """
        var:machineId int,,id of machine to snapshot
        var:name str,, name to give snapshot @tags validator:name
        result:str the snapshot name

    method:listSnapshots
        """
        List the snapshots of the machine
        """
        var:machineId int,, id of the machine
        result:list, list with the available snapshots

    method:deleteSnapshot
        """
        Delete a snapshot of the machine
        """
        var:machineId int,, id of the machine
        var:epoch str,, epoch time of snapshot
        result:str

    method:rollbackSnapshot
        """
        Rollback a snapshot of the machine
        """
        var:machineId int,, id of the machine
        var:epoch str,, epoch time of snapshot
        result:str

    method:createTemplate
        """
        Create a template from the active machine
        """
        var:machineId int,, id of the machine
        var:templatename str,, name of the template
        var:basename str,, snapshot id on which the template is based @tags: optional
        result:bool, True if template was created

#    method:export
#        """
#        Create an export/backup of the machine
#        """
#        var:machineId int,, id of the machine to backup
#        var:name str,, useful name for this backup
#        var:host str,, host to export(if s3)
#        var:aws_access_key str,,s3 access key
#        var:aws_secret_key str,,s3 secret key
#        var:bucket str,,s3 bucket name
#        result:jobid

    method:getConsoleUrl
        """
        Get url to connect to console
        """
        var:machineId str,, id of the machine to connect to console
        result:str, one time url used to connect ot console


    method:resize
        """
        Change the size of a machine
        """
        var:machineId int,, id of machine to resize
        var:sizeId int,,new sizeId
        result:bool

    method:clone
        """
        Clone the machine
        """
        var:machineId int,,id of the machine to clone
        var:name str,, name of the cloned machine @tags validator:name
        result:int, id of the new cloned machine

    method:getHistory
        """
        Get machine history
        """
        var:machineId int,,id of the machine
        var:size int,, number of entries to return
        result:list, list of the history of the machine

#    method:listExports
#        """
#        List exported images
#        """
#        var:machineId str,, id of the machine
#        var:status str,, filter on specific status @tags: optional
#        result:list, list of exports, each as a dict

    method:addUser
        """
        Give a registered user access rights
        """
        var:machineId int,,  id of the machine
        var:userId str,, username or emailaddress of the user to grant access
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully

    method:deleteUser
        """
        Revoke user access from the vmachine
        """
        var:machineId int,, id of the machine
        var:userId str,, id or emailaddress of the user to remove
        result:bool, True if user access was revoked from machine

    method:updateUser
        """
        Update user access rights. Returns True only if an actual update has happened.
        """
        var:machineId int,, id of the machineId
        var:userId str,, userid/email for registered users or emailaddress for unregistered users
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user access was updated successfully

    method:attachExternalNetwork
        """
        Attach a public network to the machine
        """
        var:machineId int,, id of the machine
        result:bool, True if a public network was attached to the machine

    method:detachExternalNetwork
        """
        Detach the public network from the machine
        """
        var:machineId int,, id of the machine
        result:bool, True if public network was detached from the machine

    method:addExternalUser
        """
        Give an unregistered user access rights by sending an invite email
        """
        var:machineId int,, id of the machine
        var:emailaddress str,, emailaddress of the unregistered user that will be invited
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully
