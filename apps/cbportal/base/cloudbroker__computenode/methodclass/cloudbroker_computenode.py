from JumpScale import j
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor

class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    
    """
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
        return self._changeStackStatus(name, gid, status, kwargs)

    def _changeStackStatus(self, name, gid, status, kwargs):
        stack = self.models.stack.search({'name':name, 'gid': int(gid)})[1:]
        if stack:
            stack = stack[0]
            stack['status'] = status
            self.models.stack.set(stack)
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
        stack = self.models.stack.search({'name':name, 'gid': int(gid)})[1:]
        if stack:
            self._changeStackStatus(name, gid, 'DISABLED', kwargs)
            stack = stack[0]
            machines_actor = j.apps.cloudbroker.machine
            stackmachines = self.models.vmachine.search({'stackId': stack['id']})[1:]
            for machine in stackmachines:  
                cloudspace = self.models.cloudspace.get(machine['cloudspaceId'])
                account = self.models.account.get(cloudspace.accountId)

                machines_actor.moveToDifferentComputeNode(account.name, machine['id'], targetComputeNode=None, withSnapshots=True, collapseSnapshots=False)
        return True

    def btrfs_rebalance(self, name, gid, mountpoint, uuid, **kwargs):
        """
        Rebalances the btrfs filesystem
        var:name str,, name of the computenode
        var:gid int,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool
        """
        raise NotImplemented()

