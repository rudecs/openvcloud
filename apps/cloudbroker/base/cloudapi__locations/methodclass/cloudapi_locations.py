from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth as audit


class cloudapi_locations(object):
    def __init__(self):
        self._te = {}
        self.actorname = "locations"
        self.appname = "cloudapi"
        self.osis = j.core.osis.getClientForNamespace('system')
        self._cb = None
        self._models = None

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


    @audit()
    def list(self, **kwargs):
        """
        List locations.
        result []
        """
        return self.models.location.search({})[1:]

    def getUrl(self):
        return j.application.config.get('cloudbroker.portalurl')
