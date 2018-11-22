from JumpScale import j

descr = """
Libvirt script to create a virtual machine
"""

name = "startmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, xml, vmlog_dir, netinfo):
    from CloudscalerLibcloud.utils.network import NetworkTool
    j.system.fs.createDir(vmlog_dir)
    with NetworkTool(netinfo) as net:
        return net.connection.create(machineid, xml)
