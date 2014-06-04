from JumpScale import j

descr = """
Checks vmachine disk(s)
"""

organization = 'jumpscale'
name = 'vm_disk_check'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

enable = True
async = True
log = False

def action(vm_id):
    import JumpScale.lib.qemu_img

    DISK_PATH = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vm_id, 'vm-%s-base.qcow2' % vm_id)
    return j.system.platform.qemu_img.info(DISK_PATH)