from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
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


    def _get(self, cloudspaceId):
        location = self.cb.extensions.imp.whereAmI()
        s3storagebuckets = self.models.s3user.search({'cloudspaceId':int(cloudspaceId), 'location':location})[1:]
        if len(s3storagebuckets) == 0:
            return None
        return s3storagebuckets[0]

    @authenticator.auth(acl='R')
    @audit()
    def get(self, cloudspaceId, **kwargs):
        """
        Gets the S3 details for a specific cloudspace
        param:cloudspaceId id of the space
        result list
        """
        ctx = kwargs['ctx'] 
        connectiondetails = self._get(cloudspaceId)
        if connectiondetails is None:
            ctx.start_response('404 Not Found', [])
            return 'No S3 Credentials found for this CloudSpace.'
        return connectiondetails

    @authenticator.auth(acl='R')
    @audit()
    def listbuckets(self, cloudspaceId, **kwargs):
        """
        List the storage buckets in a space.
        param:cloudspaceId id of the space
        result list
        """
        import boto
        import boto.s3.connection

        connectiondetails = self._get(cloudspaceId)
        if connectiondetails is None:
            return []

	access_key = connectiondetails['accesskey']
        secret_key = connectiondetails['secretkey']
        s3server = connectiondetails['s3url']
        conn = boto.connect_s3(access_key,secret_key,is_secure=True,host=s3server,calling_format = boto.s3.connection.OrdinaryCallingFormat())
        result = conn.get_all_buckets()
        buckets = [{'name':bucket.name, 's3url':s3server} for bucket in result]
        return buckets

