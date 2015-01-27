from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_sizes(BaseActor):
    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).

    """
    @audit()
    def list(self, cloudspaceId=None, **kwargs):
        """
        List the availabe flavors, filtering can be based on the user which is doing the request
        result list

        """
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fields = ['id', 'name', 'vcpus', 'memory', 'description', 'CU', 'disks']
        results  = self.models.size.search({'$fields': fields, 'gid':cloudspace.gid})[1:]
        return results
