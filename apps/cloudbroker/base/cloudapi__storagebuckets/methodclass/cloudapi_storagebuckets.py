from JumpScale import j

class cloudapi_storagebuckets(j.code.classGetBase()):
    """
    API Actor api, this actor is the final api a enduser uses to manage storagebuckets
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="storagebuckets"
        self.appname="cloudapi"
        self._cb = None
        self._models = None
        j.logger.setLogTargetLogForwarder()

        self.osisclient = j.core.osis.getClient(user='root')
        self.osis_logs = j.core.osis.getClientForCategory(self.osisclient, "system", "log")

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    def list(self, cloudspaceId, storagebuckettype, **kwargs):
        """
        List the storage buckets in a space.
        param:cloudspaceId id of space in which machine exists
        param:storagebuckettype when not empty will filter on type types are (S3)
        result list
        """
        
        term = dict()
        query = {'fields':['id','cloudspaceId','url','name','location','accesskey']}
        query['query'] = {'term':{'cloudspaceId':cloudspaceId}}
        results = self.models.s3bucket.find(ujson.dumps(query))['result']
        storagebuckets = [res['fields'] for res in results]
        return storagebuckets
    
