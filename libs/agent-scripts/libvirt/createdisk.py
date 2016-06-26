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
    from CloudscalerLibcloud import openvstorage
    from ovs.lib.vdisk import VDiskController, PMachineList
    pmguid = PMachineList.get_by_ip(pmachineip).guid
    data = VDiskController.create_from_template(templateguid, machinename='%s/base' % vmname, devicename='image', pmachineguid=pmguid)
    filepath = j.system.fs.joinPaths('/mnt/vmstor', data['backingdevice'].lstrip('/'))
    openvstorage.truncate(filepath, size)
    return openvstorage.getUrlPath(data['backingdevice'])

