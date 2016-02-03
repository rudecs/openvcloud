[actor] @dbtype:mem,osis
    """
    API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces
    """    
    method:create
        """
        Create an extra cloudspace
        """
        var:accountId int,,id of acount this cloudspace belongs to
        var:location str,, name of cloudspace to create
        var:name str,,name of space to create
        var:access str,,username of a user which has full access to this space
        var:maxMemoryCapacity int,,max size of memory in space (in GB) @tags: optional 
        var:maxDiskCapacity int,,max size of aggregated disks (in GB) @tags: optional 
        result:int, id of created cloudspace

    method:deploy
        """
        Create VFW for cloudspace
        """
        var:cloudspaceId int,, id of the cloudspace
        result:str, status of deployment

    method:delete
        """
        Delete the cloudspace
        """
        var:cloudspaceId int,, id of the cloudspace
        result:bool, True if deletion was successful

    method:list
        """
        List all cloudspaces the user has access to
        """
        result:[], list with every element containing details of a cloudspace as a dict

    method:get
        """
        Get cloudspace details
        """
        var:cloudspaceId int,, id of the cloudspace
        result:dict, dict with cloudspace details

    method:update
        """
        Update the cloudspace name and capacity parameters
        """
        var:cloudspaceId int,, id of the cloudspace
        var:name str,, name of the cloudspace
        var:maxMemoryCapacity int,, max size of memory in space(in GB)
        var:maxDiskCapacity int,, max size of aggregated disks(in GB)
        result:int, id of updated cloudspace

    method:addUser
        """
        Give a registered user access rights
        """
        var:cloudspaceId int,, id of the cloudspace
        var:userId str,, username or emailaddress of the user to grant access
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully

    method:updateUser
        """
        Update user access rights. Returns True only if an actual update has happened.
        """
        var:cloudspaceId int,, id of the cloudspace
        var:userId str,, userid/email for registered users or emailaddress for unregistered users
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user access was updated successfully

    method:deleteUser
        """
        Revoke user access from the cloudspace
        """
        var:cloudspaceId int,, id of the cloudspace
        var:userId str,, id or emailaddress of the user to remove
        var:recursivedelete bool,False, recursively revoke access rights from related vmachines @optional
        result: bool, True if user access was revoked from cloudspace

    method:getDefenseShield
        """
        Get information about the defense shield
        """
        var:cloudspaceId int,, id of the cloudspace
        result: dict, dict with defense shield details

    method:addExternalUser
        """
        Give an unregistered user access rights by sending an invite email
        """
        var:cloudspaceId int,, id of the cloudspace
        var:emailaddress str,, emailaddress of the unregistered user that will be invited
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully