from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def prepare(self, serviceObj):
        if serviceObj.hrd.get("instance.key.priv").strip() == "":
            self._generateKeys(serviceObj)
        elif serviceObj.hrd.get("instance.key.priv"):
            privloc = "/tmp/privkey"
            publoc = '/tmp/pubkey'
            privkey = serviceObj.hrd.get("instance.key.priv")
            j.do.writeFile(privloc, privkey)
            j.do.chmod(privloc, 0o600)
            cmd = 'ssh-keygen -f %s -y -N \'\'> \'%s\'' % (privloc,publoc)
            j.do.execute(cmd)
            j.do.chmod(publoc, 0o600)
            pubkey = j.do.readFile(publoc)
            serviceObj.hrd.set("instance.key.pub", pubkey)
            j.system.fs.remove(publoc)
            j.system.fs.remove(privloc)


    def _generateKeys(self,serviceObj):
        keyloc = "/tmp/id_dsa"
        j.system.process.executeWithoutPipe("ssh-keygen -t dsa -f %s -P '' " % keyloc)
        if not j.system.fs.exists(path=keyloc):
            raise RuntimeError("cannot find path for key %s, was keygen well executed" % keyloc)

        key = j.system.fs.fileGetContents(keyloc)
        keypub = j.system.fs.fileGetContents(keyloc + ".pub")

        serviceObj.hrd.set("instance.key.pub", keypub)
        serviceObj.hrd.set("instance.key.priv", key)

        j.system.fs.remove(keyloc)
        j.system.fs.remove(keyloc+".pub")

    def configure(self, serviceObj):
        """
        create key
        """

        if serviceObj.hrd.get("instance.key.priv").strip() == "":
            self._generateKeys(serviceObj)

        return True

    def removedata(self, serviceObj):
        """
        remove key data
        """
        pass