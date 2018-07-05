from framework.api import utils

class AgentController:
    def __init__(self, api_client):
        self._api = api_client

    def executeJumpscript(self, gid, cmd, nid, organization='jumpscale', name='exec', timeout=600, **kwargs):
        return self._api.system.agentcontroller.executeJumpscript(
            gid=gid,
            nid=nid,
            timeout=timeout,
            organization=organization,
            name=name,
            args='{"cmd": "%s"}' % cmd,
            wait=True,
            all=False,
            errorreport=True,
            **kwargs
        )

    def listActiveSessions(self):
        return self._api.system.agentcontroller.listActiveSessions()

    def listSessions(self):
        return self._api.system.agentcontroller.listSessions()

    def loadJumpscripts(self, path):
        return self._api.system.agentcontroller.loadJumpscripts(path=path)


