from JumpScale import j

descr = """
Script to assure the Libvirt network and the corresponding vxLan exists
"""

name = "createnetwork"
category = "libvirt"
organization = "greenitglobe"
author = "vscalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(networkid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    networks = connection.connection.listNetworks()
    from JumpScale.lib import ovsnetconfig
    vxnet = j.system.ovsnetconfig.ensureVXNet(networkid, 'vxbackend')
    bridgename = vxnet.bridge.name
    networkinformation = {'networkname': bridgename}
    if bridgename not in networks:
        #create the bridge if it does not exist
        connection.createNetwork(bridgename, bridgename)
    return networkinformation
