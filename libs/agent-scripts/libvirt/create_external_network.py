from JumpScale import j

descr = """
Script to assure the Libvirt network and the corresponding bridge exists
"""

category = "libvirt"
organization = "greenitglobe"
author = "vscalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(vlan):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    if vlan is None or vlan == 0:
        bridgename = 'public'
    else:
        bridgename = 'ext-%04x' % vlan

    nics = j.system.net.getNics()
    if bridgename not in nics:
        extbridge = 'ext-bridge'
        if extbridge not in nics:
            extbridge = 'backplane1'
        j.system.ovsnetconfig.newVlanBridge(bridgename, extbridge, vlan)
    if not connection.checkNetwork(bridgename):
        connection.createNetwork(bridgename, bridgename)
    return bridgename
