[actor] @dbtype:mem,fs
    """
    API Check status of osis and alertservice
    """
    method:status @noauth
        """
       	check status of osis and alertservice
        """
        result:dict  #returns A json dict

