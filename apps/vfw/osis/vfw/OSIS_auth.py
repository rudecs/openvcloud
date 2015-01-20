from JumpScale import j

class AUTH():

    def load(self,osis):
        pass

    def authenticate(self,osis,method,user,passwd, session):
        if j.core.osis.cmds._authenticateAdmin(user=user,passwd=passwd,die=False):
            return True
        if method in ('get', 'find') and j.core.osis.cmds.authenticate('system', 'node', user, passwd, session):
            return True
        return False
