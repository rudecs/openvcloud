[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage storagebuckets
    """    

    method:list
        """
        List the storage buckets in a space.
        """
        var:cloudspaceId int,,id of space in which machine exists @tags: optional 
        var:type str,,when not empty will filter on type types are (S3) @tags: optional 
        result:list 
