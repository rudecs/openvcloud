from JumpScale import j

descr = """
Script to assure the Libvirt network and the corresponding vxLan exists
"""

name = "createnetwork"
category = "libvirt"
organization = "cloudscalers"
author = "vscalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(networkid):
    networkname = 'space_%s' % networkid
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    networks = connection.connection.listNetworks()
    networkinformation = {'networkname':networkname}
    from JumpScale.lib import ovsnetconfig
    vxnet = j.system.ovsnetconfig.ensureVXNet(networkid, 'vxbackend')
    if networkname not in networks:
        #create the bridge if it does not exist
        bridgename = vxnet.bridge.name
        connection.createNetwork(networkname,bridgename)
    return networkinformation



