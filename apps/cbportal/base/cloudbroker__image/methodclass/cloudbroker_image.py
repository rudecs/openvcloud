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

    def _checkimage(self, imageId, ctx):
        cbimage = self.cbcl.image.search({'referenceId': imageId})[1:]
        if not cbimage:
            if ctx:
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response('400', headers)
            return False, 'Image with id "%s" not found' % imageId, None
        cbimage = cbimage[0]
        libvirtimage = None
        if self.libvirtcl.image.exists(imageId):
            libvirtimage = self.libvirtcl.image.get(imageId)
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
        ctx = kwargs.get('ctx')
        check, result, libvirtimage = self._checkimage(imageId, ctx)
        if check:
            result['status'] = 'DESTROYED'
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
        ctx = kwargs.get('ctx')
        check, result, libvirtimage = self._checkimage(imageId, ctx)
        if check:
            if not libvirtimage:
                result['status'] = 'DESTROYED'
                return self.cbcl.image.set(result)
            if libvirtimage.status == 'DISABLED':
                result['status'] = 'CREATED'
                libvirtimage.status = 'CREATED'
                self.libvirtcl.image.set(libvirtimage)
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
        ctx = kwargs.get('ctx')
        check, result, libvirtimage = self._checkimage(imageId, ctx)
        if check:
            if not libvirtimage:
                result.status = 'DESTROYED'
                return self.cbcl.image.set(result)
            if libvirtimage.status == 'CREATED' or libvirtimage.status == '':
                result['status'] = 'DISABLED'
                libvirtimage.status = 'DISABLED'
                self.libvirtcl.image.set(libvirtimage)
                return self.cbcl.image.set(result)
            else:
                return 'Image could not be DISABLED'
        return result