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