[actor] @dbtype:mem,osis
    """
    Lists all the images. A image is a template which can be used to deploy machines.
    """
    method:list
        """
        List the availabe images, filtering can be based on the user which is doing the request
        """
        var:accountId int,, optional account id to include account images @tags: optional
        var:cloudspaceId int,, optional cloudpsace id to filer @tags: optional
        result: list


    method:delete
        """
        Delete an image
        """
        var:imageId int,, id of the image to delete
        var:permanently bool,False, whether to completly delete the image @optional
        result:bool, True if image was deleted successfully

    method:restore
        """
        restore image
        """
        var:imageId int,,id of image to be restored
        result:bool

