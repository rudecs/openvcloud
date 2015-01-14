from JumpScale import j

descr = """
Prepares a live-migration action for a vm by getting disks info
"""

name = "vm_livemigrate_getdisksinfo"
category = "cloudbroker"
organization = "cloudscalers"
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"
async = True

def action(vmId, chain=False):
    import JumpScale.lib.qemu_img
    result = list() if chain else dict()
    disks_dir = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vmId)
    disks = j.system.fs.listFilesInDir(disks_dir)
    for disk in disks:
        disk_info = j.system.platform.qemu_img.info(disk, chain=chain)
        if not chain:
            result[disk_info['image']] = disk_info
        else:
            result.append(disk_info)
    return result
