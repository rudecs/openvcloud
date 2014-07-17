from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
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


    @audit()
    def list(self, accountid, **kwargs):
        """
        List the availabe images, filtering can be based on the user which is doing the request
        """
        fields = ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        if accountid:
            query = {'status': 'CREATED', 'accountId': {"$in": [0, int(accountid)]}}
        else:
            query = {'status': 'CREATED', 'accountId': 0}
        results = self.models.image.search(query)[1:]
        self.cb.extensions.imp.filter(results, fields)
        return results

    @audit()
    def delete(self, imageid, **kwargs):
        """
        Delete a image, you need to have Write access on the image
        param:imageid id of the image to delete
        result
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

