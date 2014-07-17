from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
import ujson


class cloudapi_sizes(object):
    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).

    """
    def __init__(self):

        self._te = {}
        self.actorname = "sizes"
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

    @audit()
    def list(self, **kwargs):
        """
        List the availabe flavors, filtering can be based on the user which is doing the request
        result list

        """
        fields = ['id', 'name', 'vcpus', 'memory', 'description', 'CU', 'disks']
        results  = self.models.size.search({})[1:]
        self.cb.extensions.imp.filter(results, fields)
        return results
