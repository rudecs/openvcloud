from JumpScale import j

descr = """
Set password for user
"""

name = "vfs_set_password_routeros"
category = "vfw"
organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True

def action(fwobject, username, password):
    import JumpScale.baselib.remote
    from JumpScale.lib.routeros.RouterOS import RouterOS

    host = fwobject['host']
    api_username = fwobject['username']
    api_password = fwobject['password']

    ro = RouterOS(host, api_username, api_password)
    ro.executeScript('/user set %s password=%s' %  (username, password))
    return True
