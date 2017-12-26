from JumpScale import j
from JumpScale.portal.portal import exceptions
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_image(BaseActor):
    def _checkimage(self, imageId):
        if not self.models.image.exists(imageId):
            raise exceptions.BadRequest('Image with id "%s" not found' % imageId)
        return self.models.image.get(imageId)

    @auth(['level1', 'level2', 'level3'])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        self.models.image.updateSearch({'id': imageId}, {'$set': {'status': 'DESTROYED'}})
        self.models.stack.updateSearch({'images': imageId}, {'$pull': {'images': imageId}})
        return True

    @auth(['level1', 'level2', 'level3'])
    def enable(self, imageId, **kwargs):
        """
        Enable an image
        param:imageId id of image
        result bool
        """
        image = self._checkimage(imageId)
        if image.status == 'DESTROYED':
            raise exceptions.BadRequest('Can not enable a destroyed image')
        self.models.image.updateSearch({'id': imageId}, {'$set': {'status': 'ENABLED'}})

    @auth(['level1', 'level2', 'level3'])
    def disable(self, imageId, **kwargs):
        """
        Disable an image
        param:imageId id of image
        result bool
        """
        image = self._checkimage(imageId)
        if image.status == 'DESTROYED':
            raise exceptions.BadRequest('Can not disable a destroyed image')
        self.models.image.updateSearch({'id': imageId}, {'$set': {'status': 'DISABLED'}})

    @auth(['level1', 'level2', 'level3'])
    def updateNodes(self, imageId, enabledStacks, **kwargs):
        enabledStacks = enabledStacks or list()
        image = self._checkimage(imageId)
        enabledStacks = [int(x) for x in enabledStacks]
        self.models.stack.updateSearch({'id': {'$in': enabledStacks}}, {'$addToSet': {'images': image.id}})
        self.models.stack.updateSearch({'id': {'$nin': enabledStacks}}, {'$pull': {'images': image.id}})
        return True
