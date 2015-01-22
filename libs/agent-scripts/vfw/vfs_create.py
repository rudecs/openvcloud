from JumpScale import j

descr = """
Creates an LXC machine from template
"""

name = "vfs_create"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = []


def action(name, base='base'):
    import JumpScale.lib.lxc
    import JumpScale.baselib.remote

    templatespath = j.system.fs.joinPaths('/opt', 'lxc', 'templates')
    j.system.platform.lxc.create(name=name, base=j.system.fs.joinPaths(templatespath, base))
    j.system.platform.lxc.start(name)
    ipaddress = j.system.platform.lxc.getIp(name)
    remoteApi = j.remote.cuisine.api
    # assuming template password is rooter
    j.remote.cuisine.fabric.env['password'] = 'rooter'
    remoteApi.connect(ipaddress)
    status = remoteApi.run('service ssh status')
    if 'running' not in status:
        j.errorconditionhandler.raiseOperationalWarning("SSH is not running on machine '%s'" % name)
    #set root password
    passwd = j.application.config.get('system.superadmin.passwd')
    remoteApi.run("echo -e '%(passwd)s\n%(passwd)s'|passwd root" % {'passwd': passwd})
    return True

