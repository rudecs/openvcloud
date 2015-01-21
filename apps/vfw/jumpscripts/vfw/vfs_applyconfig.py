from JumpScale import j

descr = """
Applies the rules in the passed fwobject to the given LXC machine name
"""

name = "vfs_applyconfig"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = []


def action(name, fwobject):
    import JumpScale.lib.lxc
    import JumpScale.lib.nginx
    import JumpScale.lib.shorewall
    import JumpScale.baselib.remote
    
    host = j.system.platform.lxc.getIp(name)
    password = j.application.config.get('system.superadmin.passwd')

    nginxclient = j.system.platform.nginx.get(host, password)
    shorewallclient = j.system.platform.shorewall.get(host, password)

    nginxclient.configure(fwobject)
    shorewallclient.configure(fwobject)

    return True
