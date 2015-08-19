from JumpScale import j
from JumpScale.portal.portal.auth import auth
import JumpScale.grid.agentcontroller

class cloudbroker_grid(object):

    def __init__(self):
        self.acl = j.clients.agentcontroller.get()

    @auth(['level1', 'level2', 'level3'])
    def purgeLogs(self, gid, age='-3d', **kwargs):
        return self.acl.executeJumpscript('cloudscalers', 'logs_purge', args={'age': age}, gid=gid, role='master', wait=False)['result']

    @auth(['level1', 'level2', 'level3'])
    def checkVMs(self, **kwargs):
        sessions = self.acl.listSessions()
        for nodeid, roles in sessions.iteritems:
            if 'master' in roles:
                gid = int(nodeid.split('_')[0])
                self.acl.executeJumpscript('jumpscale', 'vms_check', gid=gid, role='master', wait=False)
                return True
        return False
