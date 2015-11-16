from JumpScale import j

descr = """
Release lease
"""

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
    if isinstance(macaddress, list):
        macs = macaddress
    else:
        macs = [macaddress]
    for mac in macs:
        ro.removeLease(mac.upper())
    return True
