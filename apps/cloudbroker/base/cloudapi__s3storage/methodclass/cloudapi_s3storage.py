from JumpScale import j
from cloudbrokerlib import authenticator, enums
import ujson

class cloudapi_s3storage(j.code.classGetBase()):
    """
    API Actor api, this actor is the final api a enduser uses to manage storagebuckets
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="s3storage"
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

    @authenticator.auth(acl='R')
    def listbuckets(self, cloudspaceId, **kwargs):
        
        """
        List the storage buckets in a space.
        param:cloudspaceId id of the space
        result list
        """
        return []
    

    @authenticator.auth(acl='R')
    def get(self, cloudspaceId, **kwargs):
        """
        Gets the S3 details for a specific cloudspace
        param:cloudspaceId id of the space
        result list
        """
        ctx = kwargs['ctx'] 
        term = dict()
        
        query = {'fields':['id','cloudspaceId','s3url','name','location','accesskey','secretkey']}
        query['query'] = {'term':{'cloudspaceId':cloudspaceId}}
        results = self.models.s3user.find(ujson.dumps(query))['result']
        s3storagebuckets = [res['fields'] for res in results]
        if len(s3storagebuckets) == 0:
            ctx.start_response('404 Not Found', [])
            return 'No S3 Credentials found for this CloudSpace.'
        return s3storagebuckets[0]
