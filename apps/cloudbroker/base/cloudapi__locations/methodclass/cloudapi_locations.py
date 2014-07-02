from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit


class cloudapi_locations(object):
    def __init__(self):
        self._te = {}
        self.actorname = "locations"
        self.appname = "cloudapi"
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
        locations = self.cb.extensions.imp.getLocations()
        return locations

