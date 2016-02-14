[actor] @dbtype:mem,fs
    """
    iaas manager
    """
    method:syncAvailableImagesToCloudbroker
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        """
        result:boolean

    method:addPublicNetwork
        """
        Adds a public network range to be used for cloudspaces
        """
        var:gid int,, id of grid
        var:network str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:gateway str,, gateway of the subnet
        var:startip str,, first free ip in network range
        var:endip str,, last free ip in network range

    method:addPublicIPv4IPS
        """
        Adds a public network range to be used for cloudspaces
        """
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:freeips list,, list of ips to mark as free in the subnet

    method:removePublicIPv4IPS
        """
        Adds a public network range to be used for cloudspaces
        """
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:freeips list,, list of ips to mark as free in the subnet
        
    method:syncAvailableSizesToCloudbroker
        """
        synchronize IaaS Sizes/flavors from the libcloud model to the cloudbroker model
        """
        result:boolean
