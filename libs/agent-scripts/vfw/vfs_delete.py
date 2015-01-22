from JumpScale import j

descr = """Deletes an LXC machine"""

name = "vfs_delete"
category = "vfw"
organization = "jumpscale"
author = "zains@incubaid.com"
license = "bsd"
version = "1.0"
roles = []

def action(name):
    import JumpScale.lib.lxc
    
    j.system.platform.lxc.destroy(name)
    return True
