from JumpScale import j
from JumpScale.portal.portal.auth import auth
import JumpScale.grid.osis

class cloudbroker_computenode(j.code.classGetBase()):
    """
    Operator actions for handling interventsions on a computenode
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="ComputeNode"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')

    @auth(['level1', 'level2'])
    def setStatus(self, name, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        stacks = self.cbcl.stack.simpleSearch({'referenceId': name})
        statusses = ['ENABLED', 'DISABLED', 'OFFLINE']
        if status not in statusses:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("400", headers)
            return 'Invalid status %s should be in %s' % (status, ', '.join(statusses))
        if stacks:
            stack = self.cbcl.stack.get(stacks[0]['id'])
            stack.status = status
            self.cbcl.stack.set(stack)
            return True
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'ComputeNode with name %s not found' % name
