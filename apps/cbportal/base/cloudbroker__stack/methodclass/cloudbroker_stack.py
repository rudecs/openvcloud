from JumpScale import j
import time
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth

class cloudbroker_stack(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="stack"
        self.appname="cloudbroker"
        self.ccl = j.core.osis.getClientForNamespace('cloudbroker')

    def _changeStack(self, stackId, status, kwargs):
        stack = self.ccl.stack.get(stackId)
        if stack:
            stack.status = status
            self.ccl.stack.set(stack)
            return stack.status
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'

    @auth(['level2','level3'], True)
    def enable(self, stackId, message, **kwargs):
        return self._changeStack(stackId, 'ENABLED', kwargs)

    @auth(['level2','level3'], True)
    def disable(self, stackId, message, **kwargs):
        return self._changeStack(stackId, 'DISABLED', kwargs)
