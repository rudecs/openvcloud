[actor] @dbtype:mem,fs
    """
    Operator actions to perform specific diagnostic checks on the platform
    """
    method:checkVms
        """
        Starts the vms check jumpscipt to do a ping to every VM from their virtual firewalls
        """
        result:boolean
