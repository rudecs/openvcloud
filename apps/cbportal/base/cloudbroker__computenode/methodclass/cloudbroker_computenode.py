from JumpScale import j
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor, wrap_remote

class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    
    """
    def __init__(self):
        super(cloudbroker_computenode, self).__init__()
        self._ncl = j.clients.osis.getCategory(j.core.portal.active.osis, 'system', 'node')

    @auth(['level1', 'level2', 'level3'])
    def setStatus(self, id, gid, status, **kwargs):
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
            return self.disable(id, gid, '')
        return self._changeStackStatus(id, gid, status, kwargs)

    def _changeStackStatus(self, id, gid, status, kwargs):
        stack = self.models.stack.search({'id':int(id), 'gid': int(gid)})[1:]
        if stack:
            stack = stack[0]
            stack['status'] = status
            self.models.stack.set(stack)
            if status in ['ENABLED', 'DISABLED', 'OFFLINE']:
                nodes = self._ncl.search({'id':int(stack['referenceId']), 'gid':stack['gid']})[1:]
                if len(nodes) > 0:
                    node = nodes[0]
                    node['active'] =  True if status == 'ENABLED' else False
                    self._ncl.set(node)
            return stack, stack['status']
        else:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return stack, 'ComputeNode with id %s not found' % id

    @auth(['level2','level3'], True)
    def enable(self, id, gid, message, **kwargs):
        return self._changeStackStatus(id, gid, 'ENABLED', kwargs)[1]

    @auth(['level2','level3'], True)
    @wrap_remote
    def disable(self, id, gid, message, **kwargs):
        stack, status = self._changeStackStatus(id, gid, 'DISABLED', kwargs)
        if stack:
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
