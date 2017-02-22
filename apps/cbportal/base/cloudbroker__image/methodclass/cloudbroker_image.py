from JumpScale import j
from JumpScale.portal.portal import exceptions
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_image(BaseActor):
    def __init__(self):
        super(cloudbroker_image, self).__init__()
        self.libvirtcl = j.clients.osis.getNamespace('libvirt')

    def _checkimage(self, imageId):
        cbimage = self.models.image.search({'referenceId': imageId})[1:]
        if not cbimage:
            raise exceptions.BadRequest('Image with id "%s" not found' % imageId)
        cbimage = cbimage[0]
        libvirtimage = None
        if self.libvirtcl.image.exists(imageId):
            libvirtimage = self.libvirtcl.image.get(imageId)
        return cbimage, libvirtimage

    @auth(['level1', 'level2', 'level3'])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        cbimage, libvirtimage = self._checkimage(imageId)
        cbimage['status'] = 'DESTROYED'
        self.models.image.set(cbimage)
        images = self.models.image.search({'referenceId': imageId})[1:]
        for image in images:
            self.models.stack.updateSearch({'images': image['id']}, {'$pull': {'images': image['id']}})
        if libvirtimage:
            libvirtimage.status = 'DESTROYED'
            self.libvirtcl.image.set(libvirtimage)
        return True

    @auth(['level1', 'level2', 'level3'])
    def enable(self, imageId, **kwargs):
        """
        Enable an image
        param:imageId id of image
        result bool
        """
        cbimage, libvirtimage = self._checkimage(imageId)
        if not libvirtimage:
            cbimage['status'] = 'DESTROYED'
            return self.models.image.set(cbimage)
        if libvirtimage.status == 'DISABLED':
            cbimage['status'] = 'CREATED'
            libvirtimage.status = 'CREATED'
            self.libvirtcl.image.set(libvirtimage)
            return self.models.image.set(cbimage)
        else:
            return 'Image was not DISABLED'

    @auth(['level1', 'level2', 'level3'])
    def disable(self, imageId, **kwargs):
        """
        Disable an image
        param:imageId id of image
        result bool
        """
        cbimage, libvirtimage = self._checkimage(imageId)
        if not libvirtimage:
            cbimage['status'] = 'DESTROYED'
            return self.models.image.set(cbimage)
        if libvirtimage.status == 'CREATED' or libvirtimage.status == '':
            cbimage['status'] = 'DISABLED'
            libvirtimage.status = 'DISABLED'
            self.libvirtcl.image.set(libvirtimage)
            return self.models.image.set(cbimage)
        else:
            return 'Image could not be DISABLED'

    @auth(['level1', 'level2', 'level3'])
    def updateNodes(self, imageId, enabledStacks, **kwargs):
        enabledStacks = enabledStacks or list()
        referenceId = imageId

        def getResource(stack):
            resourceid = '%(gid)s_%(referenceId)s' % stack
            return self.libvirtcl.resourceprovider.get(resourceid)

        enabledStacks = [int(x) for x in enabledStacks]
        images = self.models.image.search({'referenceId': referenceId})[1:]
        if not images:
            raise exceptions.BadRequest("Image Unavailable, is it synced?")
        image = images[0]
        for stack in self.models.stack.search({'images': image['id']})[1:]:
            resourceprovider = getResource(stack)
            if stack['id'] not in enabledStacks:
                if image['id'] in stack['images']:
                    stack['images'].remove(image['id'])
                    self.models.stack.set(stack)
                if referenceId in resourceprovider.images:
                    resourceprovider.images.remove(referenceId)
                    self.libvirtcl.resourceprovider.set(resourceprovider)
            else:
                enabledStacks.remove(stack['id'])

        for stackid in enabledStacks:
            stack = self.models.stack.get(stackid)
            resourceprovider = getResource(stack.dump())
            if image['id'] not in stack.images:
                stack.images.append(image['id'])
                self.models.stack.set(stack)

            if referenceId not in resourceprovider.images:
                resourceprovider.images.append(referenceId)
                self.libvirtcl.resourceprovider.set(resourceprovider)

        return True
