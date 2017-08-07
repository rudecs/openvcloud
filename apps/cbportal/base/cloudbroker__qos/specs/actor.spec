
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
        var:machineMAC string,, MAC of the machine to limit @optional
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
        Limit IO for a certain disk
        total and read/write options are not allowed to be combined
        see http://libvirt.org/formatdomain.html#elementsDisks iotune section for more details
        """
        var:diskId int,, Id of the disk to limit
        var:iops int,, alias for total_iops_sec for backwards compatibility @optional
        var:total_bytes_sec int,, ... @optional
        var:read_bytes_sec int,, ... @optional
        var:write_bytes_sec int,, ... @optional
        var:total_iops_sec int,, ... @optional
        var:read_iops_sec int,, ... @optional
        var:write_iops_sec int,, ... @optional
        var:total_bytes_sec_max int,, ... @optional
        var:read_bytes_sec_max int,, ... @optional
        var:write_bytes_sec_max int,, ... @optional
        var:total_iops_sec_max int,, ... @optional
        var:read_iops_sec_max int,, ... @optional
        var:write_iops_sec_max int,, ... @optional
        var:size_iops_sec int,, ... @optional
        result:bool

    method:limitCPU
        """
        Limit CPU quota
        """
        var:machineId int,, Id of the machine to limit
        result:bool
