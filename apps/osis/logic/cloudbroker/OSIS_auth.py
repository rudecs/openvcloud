from JumpScale import j
import ujson

class AUTH():

    def load(self,osis):
        pass
        
    def authenticate(self,osis,method,user,passwd):
        if j.core.osis.cmds._authenticateAdmin(user=user,passwd=passwd):
            return True
        if user=="node" and method in ["set","get"]:
            if j.core.osis.nodeguids.has_key(passwd):
                return True
        return False
