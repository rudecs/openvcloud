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
    def setStatus(self, name, gid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        statusses = ['ENABLED', 'DISABLED', 'OFFLINE']
        if status not in statusses:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("400", headers)
            return 'Invalid status %s should be in %s' % (status, ', '.join(statusses))
        if status == 'DISABLED':
            return self.disable(name, gid, '')
        return self._changeStackStatus(name, gid, status)

    def _changeStackStatus(self, name, gid, status, kwargs):
        #TODO use gid
        stack = self.cbcl.stack.simpleSearch({'referenceId':name})
        if stack:
            stack = stack[0]
            stack['status'] = status
            self.cbcl.stack.set(stack)
            return stack['status']
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'ComputeNode with name %s not found' % name

    @auth(['level2','level3'], True)
    def enable(self, name, gid, message, **kwargs):
        return self._changeStackStatus(name, gid, 'ENABLED', kwargs)

    @auth(['level2','level3'], True)
    def disable(self, name, gid, message, **kwargs):
        #TODO use gid
        stack = self.cbcl.stack.simpleSearch({'referenceId':name})
        if stack:
            stack = stack[0]
            machines_actor = j.core.portal.active.actorsloader.getActor('cloudbroker__machine')
            stackmachines = self.cbcl.vmachine.simpleSearch({'stackId': stack['id']})
            for machine in stackmachines:  
                cloudspace = self.cbcl.cloudspace.get(machine['cloudspaceId'])
                account = self.cbcl.account.get(cloudspace.accountId)

                machines_actor.moveToDifferentComputeNode(account.name, machine['id'], targetComputeNode=None, withSnapshots=True, collapseSnapshots=False)
        return self._changeStackStatus(name, gid, 'DISABLED')