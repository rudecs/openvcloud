[actor] @dbtype:mem,fs
    """
    Operator actions to perform interventions on cloudspaces
    """
    method:destroy
        """
        destroy a cloudspace
        Destroys its machines, vfws and routeros
        """
        var:accountname str,,name of account
        var:cloudspaceName str,,name of cloudspace
        var:cloudspaceId str,,ID of cloudspace
        var:reason str,, reason for destroying the cloudspace

    method:moveVirtualFirewallToFirewallNode
        """
        move the virtual firewall of a cloudspace to a different firewall node
        """
        var:cloudspaceId int,, id of the cloudspace
        var:targetNode str,, name of the firewallnode the virtual firewall has to be moved to

    method:restoreVirtualFirewall
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
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
        param:accountname var,, name of account to create space for
        param:name var,, name of space to create
        param:access var,, username which have full access to this space
        param:maxMemoryCapacity int,, max size of memory in space (in GB)
        param:maxDiskCapacity int,, max size of aggregated disks (in GB)
