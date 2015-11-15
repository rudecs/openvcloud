[actor] @dbtype:mem,fs
    """
    Operator actions to perform interventions on cloudspaces
    """
    method:destroy
        """
        destroy a cloudspace
        Destroys its machines, vfws and routeros
        """
        var:accountId int,,id of account
        var:cloudspaceId str,,ID of cloudspace
        var:reason str,, reason for destroying the cloudspace

    method:moveVirtualFirewallToFirewallNode
        """
        move the virtual firewall of a cloudspace to a different firewall node
        """
        var:cloudspaceId int,, id of the cloudspace
        var:targetNid int,, name of the firewallnode the virtual firewall has to be moved to

    method:resetVFW
        """
        Reset VFW
        """
        var:cloudspaceId int,, id of the cloudspace

    method:deployVFW
        """
        Deploy VFW
        """
        var:cloudspaceId int,, id of the cloudspace

    method:addExtraIP
        """
        Adds an available public IP address
        """
        var:cloudspaceId int,, id of the cloudspace
        var:ipaddress str,, only needed if a specific IP address needs to be assigned to this space @optional

    method:removeIP
        """
        Removed a public IP address from the cloudspace
        """
        var:cloudspaceId int,, id of the cloudspace
        var:ipaddress str,, public IP address to remove from this cloudspace

    method:create
        """
        Create a cloudspace for given account
        """
        var:accountId int,, name of account to create space for
        var:name str,, name of space to create
        var:access str,, username which have full access to this space
        var:maxMemoryCapacity int,, max size of memory in space (in GB)
        var:maxDiskCapacity int,, max size of aggregated disks (in GB)

    method:destroyVFW
        """
        Destroy VFW of this cloudspace
        """
        var:cloudspaceId int,,Id of the cloudspace

    method:updateName
        """
        Update name of the cloudspace
        """
        var:cloudspaceId int,,Id of the cloudspace
        var:newname str,,New name of the cloudspace

    method:addUser
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        """"
        var:cloudspaceId int,,Id of the cloudspace
        var:username str,,name of the user to be given rights
        var:accesstype str,, R or W

    method:deleteUser
        """
        Delete user from account.
        """"
        var:cloudspaceId int,,Id of the cloudspace
        var:username str,,name of the user to be removed

    method:deletePortForward
        """
        Deletes a port forwarding rule for a machine
        """
        var:cloudspaceId int,, ID of cloudspace
        var:ruleId int,,Portforwarding rule id
