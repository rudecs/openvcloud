from JumpScale import j

descr = """
Libvirt script to create a machine
"""

name = "createmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'hypervisor'


def action(machinexml, vmlog_dir, netinfo):
    from CloudscalerLibcloud.utils.network import NetworkTool
    j.system.fs.createDir(vmlog_dir)
    with NetworkTool(netinfo) as net:
        if not net.connection.check_machine(machinexml):
            return -1
        return net.connection.create_machine(machinexml)
