[actor] @dbtype:mem,redis,fs
    """
    List Existing publicipv4pool
    """
    method:list
        """
        """
        var:accountId int,, optional account id to include account specific publicpools @tags: optional
        result:bool
