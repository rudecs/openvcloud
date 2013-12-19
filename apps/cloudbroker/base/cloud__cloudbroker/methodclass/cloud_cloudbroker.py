from JumpScale import j
json = j.db.serializers.ujson

class cloud_cloudbroker(object):
    """
    iaas manager

    """
    def __init__(self):

        self._te = {}
        self.actorname = "cloudbroker"
        self.appname = "cloud"
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    def updateImages(self, **kwargs):
        """
        This is a internal function to update the local images of the cloudbroker
        result 
        """
        stacks = self.models.stack.list()
        for stack in stacks:
            self.cb.extensions.imp.stackImportImages(stack)


