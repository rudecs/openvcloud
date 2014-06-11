from JumpScale import j
import JumpScale.grid.osis
json = j.db.serializers.ujson
from JumpScale.portal.portal.auth import auth

class cloudbroker_ComputeNode(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname = "ComputeNode"
        self.appname = "cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    
    @auth(['level2'])
    def setStatus(self, name, status, **kwargs):
        """
        Set the computenode status, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available'
        param:name  name of the computenode
        param:status status (ENABLED, DISABLED, HALTED).
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