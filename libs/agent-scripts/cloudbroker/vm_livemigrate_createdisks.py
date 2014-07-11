from JumpScale import j

descr = """
Prepares a live-migration action for a vm by creating disks
"""

name = "vm_livemigrate_createdisks"
category = "cloudbroker"
organization = "cloudscalers"
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"
async = True

def action(vm_id, disks_info):
    import JumpScale.lib.qemu_img
    def _create_disk(diskpath):
        disk_info = disks_info[diskpath]
        if 'backing file' in disk_info:
            if j.system.fs.exists(disk_info['backing file']):
                if not j.system.fs.exists(disk_info['image']):
                    j.system.platform.qemu_img.create(disk_info['image'], 'qcow2', disk_info['virtual size'], baseImage=disk_info['backing file'])
            else:
                _create_disk(disk_info['backing file'])
                _create_disk(disk_info['image'])

    disks_dir = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vm_id)
    j.system.fs.createDir(disks_dir)
    for diskpath in disks_info:
        _create_disk(diskpath)