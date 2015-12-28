from JumpScale import j
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
import random
import urlparse

class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    
    """
    def __init__(self):
        super(cloudbroker_computenode, self).__init__()
        self._ncl = j.clients.osis.getCategory(j.core.portal.active.osis, 'system', 'node')
        self.acl = j.clients.agentcontroller.get()


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
            return exceptions.BadRequest('Invalid status %s should be in %s' % (status, ', '.join(statusses)))
        if status == 'ENABLED':
            stacks = self.models.stack.search({'id':int(id), 'gid': int(gid)})[1:]
            if not stacks:
                raise exceptions.NotFound('ComputeNode with id %s not found' % id)
            stack = stacks[0]
            if stack['status'] not in ('OFFLINE', 'ENABLED'):
                raise exceptions.PreconditionFailed("Can not enable ComputeNode in state %s" % (stack['status']))

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
            return stack['status']
        else:
            raise exceptions.NotFound('ComputeNode with id %s not found' % id)

    @auth(['level2','level3'], True)
    def enable(self, id, gid, message, **kwargs):
        return self._changeStackStatus(id, gid, 'ENABLED', kwargs)[1]

    @auth(['level2','level3'], True)
    @wrap_remote
    def disable(self, id, gid, message, **kwargs):
        stacks = self.models.stack.search({'gid': gid, 'status': 'ENABLED'})[1:]
        if not stacks:
            raise exceptions.PreconditionFailed("Disabling stack not possible when there are no other enabled stacks")
        stack = self._changeStackStatus(id, gid, 'DISABLED', kwargs)
        otherstack = random.choice(filter(lambda x: x['id'] != id, stacks))
        args = {'storageip': urlparse.urlparse(stack['apiUrl']).hostname}
        job = self.acl.executeJumpscript('cloudscalers', 'ovs_put_node_offline',
                                         nid=int(otherstack['referenceId']), gid=otherstack['gid'],
                                         args=args)
        if job['state'] != 'OK':
            raise exceptions.Error("Failed to put storage node offline")
        if stack:
            machines_actor = j.apps.cloudbroker.machine
            stackmachines = self.models.vmachine.search({'stackId': stack['id'], 'status':
                                                                    {'$nin': ['DESTROYED', 'ERROR']}
                                                         })[1:]
            for machine in stackmachines:  
                machines_actor.moveToDifferentComputeNode(machine['id'], reason="Disabling source", force=True)
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
