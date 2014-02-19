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


    def list(self, accountid, **kwargs):
        """
        List the availabe images, filtering can be based on the user which is doing the request
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        query = {'fields': ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId']}
        query['query'] = {'term': {"accountId": 0}}
        results = self.models.image.find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        if accountid:
            query['query'] = {'term': {"accountId": accountid}}
            results = self.models.image.find(ujson.dumps(query))['result']
            images = images + [res['fields'] for res in results]
        return images

    def delete(self, imageid, **kwargs):
        """
        Delete a image, you need to have Write access on the image
        param:imageid id of the image to delete
        result 
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")


 
