from JumpScale import j

class cloudapi_storagebuckets(j.code.classGetBase()):
    """
    API Actor api, this actor is the final api a enduser uses to manage storagebuckets
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="storagebuckets"
        self.appname="cloudapi"
        #cloudapi_storagebuckets_osis.__init__(self)
    

        pass

    def list(self, cloudspaceId, type, **kwargs):
        """
        List the storage buckets in a space.
        param:cloudspaceId id of space in which machine exists
        param:type when not empty will filter on type types are (S3)
        result list
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")
    
