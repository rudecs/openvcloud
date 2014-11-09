from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_locations(BaseActor):
    @audit()
    def list(self, **kwargs):
        """
        List locations.
        result []
        """
        return self.models.location.search({})[1:]

    def getUrl(self):
        return j.application.config.get('cloudbroker.portalurl')
