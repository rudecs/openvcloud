from JumpScale import j
import JumpScale.baselib.remote.cuisine

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        """
        will install a node over ssh
        """

        cl = self._getSSHClient(serviceObj)

        def pushkey():
            """
            will install the key on the node if not already present
            """
            priv, pub = self._getSSHKey(serviceObj)

            if pub:

                try:
                    cl.run('')  # force connection
                    result = cl.run(
                        'cat ~/.ssh/authorized_keys | grep "%s" ' % pub)
                except:
                    result = ""
                if result == "":
                    # the key is not present yet, push it
                    cl.run('mkdir -p ~/.ssh')
                    cl.run("echo '%s' >> ~/.ssh/authorized_keys" % pub)
        j.actions.start(name="pushkey", description='pushkey',
                        action=pushkey, stdOutput=True, serviceObj=serviceObj)

        # only do the rest if we want to install jumpscale
        if not serviceObj.hrd.getBool('instance.jumpscale'):
            return

        def update():
            cl.sudo("apt-get update")
        j.actions.start(name="update", description='update', action=update,
                        stdOutput=True, serviceObj=serviceObj)

        def upgrade():
            cl.sudo("apt-get upgrade -y")
        j.actions.start(name="upgrade", description='upgrade', action=upgrade,
                        stdOutput=True, serviceObj=serviceObj)

        def extra():
            cl.sudo("apt-get install byobu curl -y")
        j.actions.start(name="extra", description='extra', action=extra,
                        stdOutput=True, serviceObj=serviceObj)

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
        self.execute(serviceObj, "killall tmux;killall python;echo")
        # j.do.execute("rm -rf /opt")
        return True

    def execute(self, serviceObj, cmd):
        cl = self._getSSHClient(serviceObj)
        return cl.sudo(cmd)

    def upload(self, serviceObj, source, dest):
        sshkey, _ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        rdest = "%s:%s" % (ip, dest)
        login = serviceObj.hrd.get('instance.login', default='') or None
        if login:
            cl = self._getSSHClient(serviceObj)
            chowndir = dest
            while not cl.file_exists(chowndir):
                chowndir = j.system.fs.getParent(chowndir)
            cl.sudo("chown -R %s %s" % (login, chowndir))
        services = j.system.fs.walk(j.system.fs.getParent(source), pattern='*__*__*', return_folders=1, return_files=0)
        self._rsync(services, rdest, sshkey, port, login)

    def download(self, serviceObj, source, dest):
        sshkey, _ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")

        rsource = "%s:%s" % (ip, source)
        login = serviceObj.hrd.get('instance.login', default='') or None
        self._rsync([rsource], dest, sshkey, port, login)

    def _getSSHKey(self, serviceObj):
        keyname = serviceObj.hrd.get("instance.sshkey")
        if keyname != "":
            sshkeyHRD = j.application.getAppInstanceHRD("sshkey", keyname, parent=None)
            return (sshkeyHRD.get("instance.key.priv"), sshkeyHRD.get("instance.key.pub"))
        else:
            return (None, None)

    def _getSSHClient(self, serviceObj):
        c = j.remote.cuisine

        ip = serviceObj.hrd.get('instance.ip')
        port = serviceObj.hrd.getInt('instance.ssh.port')
        login = serviceObj.hrd.get('instance.login', default='')
        password = serviceObj.hrd.get('instance.password', default='')
        priv, _ = self._getSSHKey(serviceObj)
        if priv:
            c.fabric.env["key"] = priv

        if password == "" and priv is None:
            raise RuntimeError(
                "can't connect to the node, should provide or password or a key to connect")

        connection = c.connect(ip, port, passwd=password)
        connection.fabric.api.env['shell'] = serviceObj.hrd.get('instance.ssh.shell', "/bin/bash -l -c")

        if login != '':
            connection.fabric.api.env['user'] = login
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
