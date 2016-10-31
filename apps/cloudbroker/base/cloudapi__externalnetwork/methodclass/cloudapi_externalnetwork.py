from JumpScale import j
from cloudbrokerlib.baseactor import BaseActor


class cloudapi_externalnetwork(BaseActor):


    def list(self, accountId, **kwargs):
        """
        result 
        """
        query = {}
        if accountId:
            query['accountId'] = {'$in': [None, accountId]}
        return self.models.externalnetwork.search({'$query': query, '$fields': ['id', 'name']})[1:]
