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
roles = ["*"]


def action(networkid):
    networkname = 'space_%s' % networkid
    
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    networks = connection.connection.listNetworks()
    networkinformation = {'networkname':networkname}
    if networkname not in networks:
    	bridgename = 'br-%s' % networkid
    	#create the bridge if it does not exist
    	from JumpScale.lib import ovsnetconfig
    	#TODO: check if the bridge does not exist yet
    	#TODO: check if the vxLan does not exist yet
    	vxlan = j.system.ovsnetconfig.newVXLan(networkid)
    	j.system.ovsnetconfig.newBridge(bridgename, vxlan)

    	connection.createNetwork(networkname,bridgename)
    	
    return networkinformation



