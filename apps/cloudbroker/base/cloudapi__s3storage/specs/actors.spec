[actor] @dbtype:mem,osis
    """
    API Actor api, this actor is the final api a enduser uses to manage S3 storage
    """

    method:listbuckets
        """
        List the S3 buckets in a space.
        """
        var:cloudspaceId int,,id of the space
        result:list

    method:get
        """
        Gets the S3 details for a specific cloudspace
        """
        var:cloudspaceId int,, id of the space
        result:dict
