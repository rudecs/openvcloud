from JumpScale import j
import JumpScale.grid.osis
json = j.db.serializers.ujson

class cloudbroker_iaas(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname = "cloudbroker"
        self.appname = "iaas"
        self._cb = None
        self._models = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    def updateImages(self, **kwargs):
        """
        Update the local images of the cloudbroker
        result 
        """
        stacks = self.models.stack.list()
        for stack in stacks:
            self.cb.extensions.imp.stackImportImages(stack)

    def setStackStatus(self, statckid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        if self.models.stack.exists(statckid):
            stack = self.models.stack.get(statckid)
            stack.status = status
            self.models.stack.set(stack)
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Stack ID not found'
    