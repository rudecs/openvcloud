from JumpScale import j
from cloudapi_sizes_osis import cloudapi_sizes_osis
import ujson


class cloudapi_sizes(cloudapi_sizes_osis):

    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).

    """

    def __init__(self):

        self._te = {}
        self.actorname = "sizes"
        self.appname = "cloudapi"
        cloudapi_sizes_osis.__init__(self)
        self._cb = None
        self._models = None


        pass

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

    def list(self, **kwargs):
        """
        List the availabe flavors, filtering can be based on the user which is doing the request
        result list

        """
        term = dict()
        query = {'fields': ['id', 'name', 'vcpus', 'memory', 'description', 'CU', 'disks']}
        results  = self.models.size.find(ujson.dumps(query))['result']
        sizes = [res['fields'] for res in results]
        return sizes
