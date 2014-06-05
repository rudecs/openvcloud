from JumpScale import j
import JumpScale.grid.osis
import JumpScale.grid.agentcontroller
json = j.db.serializers.ujson

class cloudbroker_iaas(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname = "cloudbroker"
        self.appname = "iaas"

    def updateImages(self, **kwargs):
        """
        Update the local images of the cloudbroker
        result 
        """
        acc = j.clients.agentcontroller.get()
        acc.executeJumpScript('cloudscalers', 'cloudbroker_updateimages', role='cloudbroker', wait=False)

    def setStackStatus(self, statckid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        if cbcl.stack.exists(statckid):
            stack = cbcl.stack.get(statckid)
            stack.status = status
            cbcl.stack.set(stack)
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Stack ID not found'
    