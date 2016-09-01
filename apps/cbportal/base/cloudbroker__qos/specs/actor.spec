
[actor]
    """
    Provide Quality of service feature for network disk and cpu
    """

    method:limitInternalBandwith
        """
        This will put a limit on the VIF of all VMs within the cloudspace or machine
        Pass either cloudspaceId or machineId depending what you want to filter down.
        """
        var:cloudspaceId int,0, Id of the cloudspace to limit @optional
        var:machineId int,0, Id of the machineId to limit @optional
        var:rate int,, maximum speeds in kilobytes per second, 0 means unlimited
        var:burst int,, maximum burst speed in kilobytes per second, 0 means unlimited
        result:bool

    method:limitInternetBandwith
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        """
        var:cloudspaceId int,, Id of the cloudspace to limit
        var:rate int,, maximum speeds in kilobytes per second, 0 means unlimited
        var:burst int,, maximum burst speed in kilobytes per second, 0 means unlimited
        result:bool

    method:limitIO
        """
        Limit IO done on a certain disk
        """
        var:diskId int,, Id of the disk to limit
        var:iops int,, Max IO per second, 0 mean unlimited
        result:bool


    method:limitCPU
        """
        Limit CPU quota
        """
        var:machineId int,, Id of the machine to limit
        result:bool
