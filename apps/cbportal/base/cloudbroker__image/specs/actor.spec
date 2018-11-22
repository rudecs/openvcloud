[actor] @dbtype:mem,fs
    """
    image manager
    """
    method:delete
        """
        delete image
        """
        var:imageId int,,id of image to be deleted
        var:reason str,, reason for deleting the image
        var:permanently bool,False, whether to completly delete the image @optional
        result:bool

    method:deleteImages
        """
        delete images
        """
        var:imageIds list(int),,list of images to be deleted
        var:reason str,, reason for deleting the images
        var:permanently bool,False, whether to completly delete the images @optional
        result:bool

    method:restore
        """
        restore image
        """
        var:imageId int,,id of image to be restored
        var:reason str,, reason for restoring the image
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

    method:createCDROMImage
        """
        Create a CD-ROM Image from an iso
        """
        var:name str,,Name of the rescue disk
        var:url str,,URL where to download ISO from
        var:gid int,,Grid ID where this CD-ROM image should be create in
        var:accountId int,,AccountId to make the image exclusive @optional
        result:bool

    method:deleteCDROMImage
        """
        Delete a CD-ROM Image
        """
        var:diskId int,,diskId of the CD-ROM image to delete
        var:permanently bool,False, whether to completly delete the CD-ROM image, needs to be unused @optional


    method:createImage
        """
        Create a Image from url
        """
        var:name str,,Name of the rescue disk
        var:url str,,URL where to download ISO from
        var:gid int,,Grid ID where this template should be create in
        var:boottype str,,Boot type of image bios or uefi
        var:hotresize bool,False, Does this machine supports hot resize @optional
        var:imagetype str,,Image type Linux, Windows or Other
        var:username str,,Optional username for the image @optional
        var:password str,,Optional password for the image @optional
        var:accountId int,,AccountId to make the image exclusive @optional
        result:bool

    method:edit
        """
        edit a Image with id 
        """
        var:imageId int,,id of the image to edit
        var:name str,,name for the image @optional
        var:username str,,username for the image @optional
        var:password str,,password for the image @optional
        var:accountId int,,AccountId to make the image exclusive @optional
        var:hotresize bool,, Does this machine supports hot resize @optional