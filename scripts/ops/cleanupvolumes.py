from JumpScale import j
import os

ccl = j.clients.osis.getNamespace('cloudbroker')

print 'Updating disk references'
for vm in ccl.vmachine.list():
    vm = ccl.vmachine.get(vm)
    for disk in vm.disks:
        disk = ccl.disk.get(disk)
        change = False
        if vm.status == 'DESTROYED':
            change = True
            disk.status = 'DESTROYED'
        if disk.type == 'B':
            change = True
            disk.referenceId = '/mnt/vmstor/vm-%s/base_image.raw' % vm.id
        if change:
            ccl.disk.set(disk)

orphans = 0
volumes = j.system.fs.walk('/mnt/vmstor', 1, '*.raw')
for volume in volumes:
    orphan = False
    if volume.startswith('/mnt/vmstor/templates'):
        continue  # skipping templates
    elif volume.startswith('/mnt/vmstor/routeros'):
        pass
    else:
        disks = ccl.disk.search({'referenceId': volume})[1:]
        for disk in disks:
            if disk['status'] == 'DESTROYED':
                orphan = True
                break
        if not disks:
            orphan = True
        if orphan:
            print volume, 'is orphan'
            orphans += 1
            os.remove(volume)

print 'Found %s/%s orphans' % (orphans, len(volumes))
