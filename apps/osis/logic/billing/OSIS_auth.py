from JumpScale import j

class AUTH():

    def load(self,osis):
        pass

    def authenticate(self,osis,method,user,passwd, session):
        if j.core.osis.cmds._authenticateAdmin(user=user,passwd=passwd):
            return True
        if j.core.osis.cmds._authenticateNode(session):
            return True
        return False
