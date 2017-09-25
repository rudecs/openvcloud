[actor] @dbtype:mem,fs
    """
    Operator actions for interventions on accounts
    """
    method:deactivateNodes
        """
        deactivate a storagerouter by moving all the storage connections
        """
        var:nids list(int),,nids of storagerouter

    method:activateNodes
        """
        Activate storagerouter 
        """
        var:nids list(int),,nids of storagerouter
