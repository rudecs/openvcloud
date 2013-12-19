from JumpScale import j
import ujson

class cloudapi_images(object):
    """
    Lists all the images. A image is a template which can be used to deploy machines.

    """
    def __init__(self):

        self._te = {}
        self.actorname = "images"
        self.appname = "cloudapi"
        self._cb = None
        self._models = None

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb


    def list(self, **kwargs):
        """
        List the availabe images, filtering can be based on the user which is doing the request

        """
        query = {'fields': ['id', 'name','description', 'type', 'UNCPath', 'size']}
        results = self.models.image.find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        return images
