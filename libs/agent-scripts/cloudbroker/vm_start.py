from JumpScale import j

descr = """
Start a signel machine
"""

name = "vm_start"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['cpunode']
queue = "hypervisor"
async = True

def action(name, networkId):
    networkname = 'space_%s' % networkId
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    networks = connection.connection.listNetworks()
    if networkname not in networks:
        #create the bridge if it does not exist
        from JumpScale.lib import ovsnetconfig
        vxnet = j.system.ovsnetconfig.ensureVXNet(networkId, 'vxbackend')
        bridgename = vxnet.bridge.name

        connection.createNetwork(networkname,bridgename)

    import libvirt
    con = libvirt.open()
    try:
        dom = con.lookupByName(name)
        state = dom.state()[0]
        if state != libvirt.VIR_DOMAIN_RUNNING:
            dom.create()
    finally:
        con.close()
