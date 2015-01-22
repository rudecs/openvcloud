from JumpScale import j

descr = """
Get IPAddress of node with macadress
"""

name = "vfs_get_ipaddress_routeros"
category = "vfw"
organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True

def action(fwobject, macaddress):
    import JumpScale.baselib.remote
    from JumpScale.lib.routeros.RouterOS import RouterOS

    host = fwobject['host']
    username = fwobject['username']
    password = fwobject['password']

    ro = RouterOS(host, username, password)
    return ro.getIpaddress(macaddress)
