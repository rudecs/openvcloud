from JumpScale import j

descr = """
Checks shorewall status
"""

name = "vfs_checkstatus"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = []


def action(name):
    import JumpScale.lib.lxc
    import JumpScale.lib.nginx
    import JumpScale.lib.shorewall
    import JumpScale.baselib.remote

    host = j.system.platform.lxc.getIp(name)
    password = j.application.config.get('system.superadmin.passwd')

    shorewallclient = j.system.platform.shorewall.get(host, password)

    return shorewallclient.status()
