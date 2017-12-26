[actor] @dbtype:mem,fs
    """
    image manager
    """
    method:delete
        """
        delete image
        """
        var:imageId int,,id of image to be deleted
        result:bool

    method:enable
        """
        enable image
        """
        var:imageId int,,id of image to be enabled
        result:bool

    method:disable
        """
        disable image
        """
        var:imageId int,,id of image to be disabled
        result:bool


    method:updateNodes
        """
        Update which nodes have this image available
        """
        var:imageId int,,id of image
        var:enabledStacks list,,list of enabled stacks @optional
        result:bool
