[actor] @dbtype:mem,fs
    """
    iaas manager
    """
    method:syncAvailableImagesToCloudbroker
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        """
        result:boolean

    method:addExternalNetwork
        """
        Adds a external network range to be used for cloudspaces
        """
        var:name str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:gateway str,, gateway of the subnet
        var:startip str,, First IP Address from the range to add
        var:endip str,, Last IP Address from the range to add
        var:gid int,, id of grid
        var:vlan int,,VLAN Tag @optional

    method:addExternalIPS
        """
        Adds a public network range to be used for cloudspaces
        """
        var:externalnetworkId int,, the id of the external network
        var:startip str,, First IP Address from the range to add
        var:endip str,, Last IP Address from the range to add

    method:changeIPv4Gateway
        """
        Updates the gateway of the pool
        """
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
        var:gateway str,, Gateway of the pool


    method:addSize
        """
        Add size to location
        """
        var:name str,, Name of the size
        var:vcpus int,,Number of vcpus
        var:memory int,,Memory in MB
        var:disksize int,,Size of bootdisk in GB

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
