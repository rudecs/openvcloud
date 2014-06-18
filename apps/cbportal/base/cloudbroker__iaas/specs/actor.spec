[actor] @dbtype:mem,fs
    """
    iaas manager
    """
    method:syncAvailableImagesToCloudbroker
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        """
        result:boolean

    method:addPublicIPv4Subnet
        """
        Adds a public network range to be used for cloudspaces
        """
        var:subnet str,, the subnet to add in CIDR notation (x.x.x.x/y)
