from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor


class cloudapi_externalnetwork(BaseActor):

    @audit(accountid="accountId")
    def list(self, accountId, **kwargs):
        """
        result 
        """
        query = {}
        if accountId:
            query['accountId'] = {'$in': [None, accountId]}
        return self.models.externalnetwork.search({'$query': query, '$fields': ['id', 'name']})[1:]
