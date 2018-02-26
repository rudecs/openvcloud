from JumpScale import j
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_node(BaseActor):
    def __init__(self):
        super(cloudbroker_node, self).__init__()
        self.scl = j.clients.osis.getNamespace('system')
        self.cbcl = j.clients.osis.getNamespace('cloudbroker')
        self.acl = j.clients.agentcontroller.get()

    def unscheduleJumpscripts(self, nid, gid, name=None, category=None):
        self.acl.scheduleCmd(gid, nid, cmdcategory="jumpscripts", jscriptid=0,
                            cmdname="unscheduleJumpscripts", args={'name': name, 'category': category},
                            queue="internal", log=False, timeout=120, roles=[])

    def scheduleJumpscripts(self, nid, gid, name=None, category=None):
        self.acl.scheduleCmd(gid, nid, cmdcategory="jumpscripts", jscriptid=0,
                            cmdname="scheduleJumpscripts", args={'name': name, 'category': category},
                            queue="internal", log=False, timeout=120, roles=[])
