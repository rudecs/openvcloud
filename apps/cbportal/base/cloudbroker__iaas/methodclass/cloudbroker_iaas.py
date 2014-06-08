from JumpScale import j
import JumpScale.grid.osis
json = j.db.serializers.ujson
from JumpScale.portal.portal.auth import auth

class cloudbroker_iaas(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname = "iaas"
        self.appname = "cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1', 'level2'])
    def updateImages(self, **kwargs):
        """
        Update the local images of the cloudbroker
        result 
        """
        stacks = self.cbcl.stack.list()
        for stack in stacks:
            self.cb.extensions.imp.stackImportImages(stack)
        return True

    @auth(['level1', 'level2'])
    def setStackStatus(self, statckid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        if self.cbcl.stack.exists(statckid):
            stack = self.cbcl.stack.get(statckid)
            stack.status = status
            self.cbcl.stack.set(stack)
            return True
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Stack ID not found'