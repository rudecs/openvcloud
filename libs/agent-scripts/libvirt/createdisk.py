from JumpScale import j

descr = """
Libvirt script to create a disk
"""

name = "createdisk"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(templateguid, vmname, size, pmachineip):
    import sys
    import os
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController, PMachineList
    pmguid = PMachineList.get_by_ip(pmachineip).guid
    data = VDiskController.create_from_template(templateguid, '%s/base' % vmname, 'image', pmguid)
    filepath = j.system.fs.joinPaths('/mnt/vmstor', data['backingdevice'].lstrip('/'))
    fd = os.open(filepath, os.O_RDWR|os.O_CREAT )
    os.ftruncate(fd, size)
    os.close(fd)
    return j.system.fs.getBaseName(data['backingdevice'].lstrip('/'))

