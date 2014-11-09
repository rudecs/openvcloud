from JumpScale import j
from JumpScale.portal.portal.auth import auth
import JumpScale.grid.agentcontroller

class cloudbroker_grid(object):

    def __init__(self):
        self.acl = j.clients.agentcontroller.get()

    @auth(['level1', 'level2'])
    def purgeLogs(self, gid, age='-3d', **kwargs):
        return self.acl.executeJumpscript('cloudscalers', 'logs_purge', args={'age': age}, role='master', wait=False)['result']

    @auth(['level1', 'level2'])
    def checkVMs(self, **kwargs):
        self.acl.executeJumpscript('jumpscale', 'vms_check', role='master', wait=False)
        return True
