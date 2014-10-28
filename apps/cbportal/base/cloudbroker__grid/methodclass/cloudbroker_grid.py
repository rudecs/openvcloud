from JumpScale import j
from JumpScale.portal.portal.auth import auth
import JumpScale.grid.agentcontroller

class cloudbroker_grid(j.code.classGetBase()):

    def __init__(self):
        self._te = dict()
        self.actorname = "grid"
        self.appname = "cloudbroker"
        self.acl = j.clients.agentcontroller.get()

    @auth(['level1', 'level2'])
    def purgeLogs(self, gid, age='-3d', **kwargs):
        return self.acl.executeJumpScript('cloudscalers', 'logs_purge', args={'age': age}, role='master', wait=False)['result']

    @auth(['level1', 'level2'])
    def checkVMs(self, **kwargs):
        self.acl.executeJumpScript('jumpscale', 'vms_check', role='master', wait=False)
        return True