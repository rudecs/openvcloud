from JumpScale import j

descr = """
Prepares a live-migration action for a vm by creating disks
"""

name = "vm_livemigrate"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"
async = True

def action(vm_id, disks_info, source_stack, target_stack, snapshots, sshkey):
    import JumpScale.lib.qemu_img
    import urlparse
    import JumpScale.baselib.remote
    import libvirt
    con = libvirt.open()
    def _create_disk(diskpath):
        disk_info = disks_info[diskpath]
        if 'backing file' in disk_info:
            if j.system.fs.exists(disk_info['backing file']):
                if not j.system.fs.exists(disk_info['image']):
                    j.system.platform.qemu_img.create(disk_info['image'], 'qcow2', disk_info['virtual size'], baseImage=disk_info['backing file'])
            else:
                _create_disk(disk_info['backing file'])
                _create_disk(disk_info['image'])

    vm_file_dir = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vm_id)
    j.system.fs.createDir(vm_file_dir)
    for diskpath in disks_info:
        _create_disk(diskpath)

    sourceip = urlparse.urlparse(source_stack['apiUrl']).hostname
    capi = j.remote.cuisine.connect(sourceip, 22)
    if sshkey:
        capi.fabric.api.env['key'] = sshkey
    capi.fabric.api.env['forward_agent'] = True

    # create machine
    iso_file_path = j.system.fs.joinPaths(vm_file_dir, 'cloud-init.vm-%s.iso' % vm_id)
    capi.fabric.operations.get(local_path=iso_file_path, remote_path=iso_file_path)

    xml = capi.run('virsh dumpxml vm-%s' % vm_id)
    domain = con.defineXML(xml)

    # do snapshots
    for snapshot in snapshots:
        snapxml = capi.run('virsh snapshot-dumpxml %(vmid)s %(ssname)s' % {'vmid': vm_id, 'ssname': snapshot['name']})
        domain.snapshotCreateXML(snapxml, libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_REDEFINE)

    capi.run('virsh migrate --live vm-%s %s --copy-storage-inc --verbose --persistent --undefinesource' % (vm_id, target_stack['apiUrl']))
    capi.run('rm -rf %s' % vm_file_dir)
