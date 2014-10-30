from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth


class cloudbroker_image(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="image"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.libvirtcl = j.core.osis.getClientForNamespace('libvirt')

    def _checkimage(self, imageId, **kwargs):
        if not self.cbcl.image.exists(imageId):
            ctx = kwargs.get('ctx')
            if ctx:
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response('400', headers)
            return False, 'Image with id "%s" not found' % imageId, None
        cbimage = self.cbcl.image.get(imageId)
        libvirtimage = None
        if self.libvirtcl.exists(cbimage.referenceId):
            libvirtimage = self.libvirtcl.get(cbimage.referenceId)
        return True, cbimage, libvirtimage

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1',])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        check, result, libvirtimage = self._checkimage(imageId, kwargs)
        if check:
            result.status = 'DESTROYED'
            self.cbcl.image.set(result)
            if libvirtimage:
                libvirtimage.status = 'DESTROYED'
                self.libvirtcl.image.set(libvirtimage)
            return True
        return result


    @auth(['level1',])
    def enable(self, imageId, **kwargs):
        """
        Enable an image
        param:imageId id of image
        result bool
        """
        check, result, libvirtimage = self._checkimage(imageId, kwargs)
        if check:
            if not libvirtimage:
                result.status = 'DESTROYED'
                return self.cbcl.image.set(result)
            if result.status == 'DISABLED':
                result.status = 'CREATED'
                libvirtimage.status = 'CREATED'
                self.libvirtcl.set(libvirtimage)
                return self.cbcl.image.set(result)
            else:
                return 'Image was not DISABLED'
        return result

    @auth(['level1',])
    def disable(self, imageId, **kwargs):
        """
        Disable an image
        param:imageId id of image
        result bool
        """
        check, result, libvirtimage = self._checkimage(imageId, kwargs)
        if check:
            if not libvirtimage:
                result.status = 'DESTROYED'
                return self.cbcl.image.set(result)
            if result.status == 'CREATED':
                result.status = 'DISABLED'
                libvirtimage.status = 'DISABLED'
                self.libvirtcl.image.set(libvirtimage)
                return self.cbcl.image.set(result)
            else:
                return 'Image could not be DISABLED'
        return result