from JumpScale import j
from cloudapi_images_osis import cloudapi_images_osis
import ujson

class cloudapi_images(cloudapi_images_osis):

    """
    Lists all the images. A image is a template which can be used to deploy machines.

    """

    def __init__(self):

        self._te = {}
        self.actorname = "images"
        self.appname = "cloudapi"
        cloudapi_images_osis.__init__(self)
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb


    def list(self, **kwargs):
        """
        List the availabe images, filtering can be based on the user which is doing the request

        """
        term = dict()
        query = {'fields': ['id', 'name','description', 'type']}
        results = self.cb.model_image_find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        return images
