from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.lib.ms1
import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self, serviceObj):
        """
        will install a node
        """
        redisCl = j.clients.redis.getByInstance('system')
        spacesecret = None

        if not redisCl.exists('cloudrobot:cloudspaces:secrets'):
            ms1_client = j.atyourservice.get(name='ms1_client', instance='main')
            ms1_client.configure()
            spacesecret = ms1_client.hrd.get('instance.param.secret')
        else:
            ms1client_hrd = j.application.getAppInstanceHRD("ms1_client","main")
            spacesecret = ms1client_hrd.get("instance.param.secret")

        def createmachine():
            _, sshkey = self._getSSHKey(serviceObj)

            machineid, ip, port = j.tools.ms1.createMachine(spacesecret, "ovc_reflector", memsize="0.5", \
                ssdsize=10, vsansize=0, description='',imagename="ubuntu.14.04.x64",delete=False, sshkey=sshkey)

            serviceObj.hrd.set("instance.param.machine.id",machineid)
            serviceObj.hrd.set("instance.param.machine.ssh.ip",ip)
            serviceObj.hrd.set("instance.param.machine.ssh.port",port)

        j.actions.start(retry=1, name="createmachine", description='createmachine', cmds='', action=createmachine, \
                        actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        # only do the rest if we want to install jumpscale
        if not serviceObj.hrd.getBool('instance.param.jumpscale'):
            return

        cl = self._getSSHClient(serviceObj)

        # def update():
        #     cl.sudo("apt-get update")
        # j.actions.start(name="update", description='update', action=update,
        #                 stdOutput=True, serviceObj=serviceObj)

        # def upgrade():
        #     cl.sudo("apt-get upgrade -y")
        # j.actions.start(name="upgrade", description='upgrade', action=upgrade,
        #                 stdOutput=True, serviceObj=serviceObj)

        def jumpscale():
            cl.sudo("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh")
        j.actions.start(name="jumpscale", description='install jumpscale',
                        action=jumpscale,
                        stdOutput=True, serviceObj=serviceObj)
        return True

    def removedata(self, serviceObj):
        """
        delete vmachine
        """
        ms1client_hrd = j.application.getAppInstanceHRD("ms1_client","main")
        spacesecret = ms1client_hrd.get("instance.param.secret")
        j.tools.ms1.deleteMachine(spacesecret, "ovc_reflector")

        return True

    def execute(self, serviceObj, cmd):
        """
        execute over ssh something onto the machine
        """
        cl = self._getSSHClient(serviceObj)
        return cl.sudo(cmd)

    def upload(self, serviceObj, source, dest):
        sshkey, _ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.param.machine.ssh.ip")
        port = serviceObj.hrd.get("instance.param.machine.ssh.port")
        rdest = "%s:%s" % (ip, dest)
        services = j.system.fs.walk(j.system.fs.getParent(source), pattern='*__*__*', return_folders=1, return_files=0)
        self._rsync(services, rdest, sshkey, port)

    def download(self, serviceObj, source, dest):
        sshkey, _ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.param.machine.ssh.ip")
        port = serviceObj.hrd.get("instance.param.machine.ssh.port")

        rsource = "%s:%s" % (ip, source)
        self._rsync([rsource], dest, sshkey, port)

    def _getSSHKey(self, serviceObj):
        keyname = serviceObj.hrd.get("instance.param.ssh.key")
        if keyname != "":
            sshkeyHRD = j.application.getAppInstanceHRD("sshkey", keyname, parent=None)
            return (sshkeyHRD.get("instance.key.priv"), sshkeyHRD.get("instance.key.pub"))
        else:
            return (None, None)

    def _getSSHClient(self, serviceObj):
        c = j.remote.cuisine

        ip = serviceObj.hrd.get('instance.param.machine.ssh.ip')
        port = serviceObj.hrd.get('instance.param.machine.ssh.port')
        # login = serviceObj.hrd.get('instance.login', default='')
        # password = serviceObj.hrd.get('instance.password', default='')
        priv, _ = self._getSSHKey(serviceObj)
        if priv:
            c.fabric.env["key"] = priv

        if priv is None:
            raise RuntimeError(
                "can't connect to the node, should provide or password or a key to connect")

        connection = c.connect(ip, port)
        connection.fabric.api.env['shell'] = serviceObj.hrd.get('instance.ssh.shell', "/bin/bash -l -c")

        # if login != '':
            # connection.fabric.api.env['user'] = login
        return connection

    def _rsync(self, sources, dest, key, port=22, login=None):
        """
        helper method that can be used by services implementation for
        upload/download actions
        """
        def generateUniq(name):
            import time
            epoch = int(time.time())
            return "%s__%s" % (epoch, name)

        sourcelist = list()
        if dest.find(":") != -1:
            # it's an upload
            dest = dest if dest.endswith("/") else dest + "/"
            sourcelist = [source.rstrip("/") for source in sources if j.do.isDir(source)]
        else:
            # it's a download
            if j.do.isDir(dest):
                dest = dest if dest.endswith("/") else dest + "/"
            sourcelist = [source.rstrip("/") for source in sources if source.find(":") != -1]

        source = ' '.join(sourcelist)
        keyloc = "/tmp/%s" % generateUniq('id_dsa')
        j.system.fs.writeFile(keyloc, key)
        j.system.fs.chmod(keyloc, 0o600)
        login = login or 'root'
        ssh = "-e 'ssh -o StrictHostKeyChecking=no -i %s -p %s -l %s'" % (
            keyloc, port, login)

        destPath = dest
        if dest.find(":") != -1:
            destPath = dest.split(':')[1]

        verbose = "-q"
        if j.application.debug:
            print("copy from\n%s\nto\n %s" % (source, dest))
            verbose = "-v"
        cmd = "rsync -a -u --exclude \"*.pyc\" --rsync-path=\"mkdir -p %s && rsync\" %s %s %s %s" % (
            destPath, verbose, ssh, source, dest)
        print cmd
        j.do.execute(cmd)
        j.system.fs.remove(keyloc)