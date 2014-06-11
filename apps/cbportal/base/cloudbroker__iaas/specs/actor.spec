[actor] @dbtype:mem,fs
    """
    iaas manager
    """
    method:syncAvailableImagesToCloudbroker
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        """
        result:boolean
