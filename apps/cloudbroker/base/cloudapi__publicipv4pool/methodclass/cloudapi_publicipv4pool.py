from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor


class cloudapi_publicipv4pool(BaseActor):

    @audit()
    def list(self, accountId, **kwargs):
        """
        result bool
        """
        query = {}
        if accountId:
            query['accountId'] = {'$in': [None, accountId]}
        return self.models.publicipv4pool.search({'$query': query, '$fields': ['id', 'name']})[1:]
