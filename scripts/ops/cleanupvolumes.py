from JumpScale import j
import os
import sys

def cleanup(ips, client_key, client_secret):
    ovs = j.clients.openvstorage.get(ips, (client_key, client_secret))
    # First delete normal disks
    while True:
        still_normal_vdisks = False
        vdisks = ovs.get('/vdisks/')['data']
        for vdisk in vdisks:
            vdisk_details = ovs.get('/vdisks/{}'.format(vdisk))
            if vdisk_details['is_vtemplate']:
                continue
            still_normal_vdisks = True
            if vdisk_details['child_vdisks_guids']:
                continue
            print "Deleting disk", vdisk_details['description']
            taskguid = ovs.delete('/vdisks/{}'.format(vdisk))
            ovs.wait_for_task(taskguid)
        if not still_normal_vdisks:
            break
    vdisks = ovs.get('/vdisks/')['data']
    for vdisk in vdisks:
        print "Deleting image", vdisk_details['description']
        taskguid = ovs.delete('/vdisks/{}'.format(vdisk))
        ovs.wait_for_task(taskguid)

answer = j.console.askString("\nAre you sure you want to delete all volumes on the storage backend?\n\n" +
                             "Type 'Yes I'm sure!' to continue.")
if answer != "Yes I'm sure!":
    print "Incorrect answer."
    sys.exit(1)

answer = j.console.askString("\nAre you very sure you want to delete all volumes on the storage backend?\n" +
                             "You see all vms will stop functioning!\n\n"
                             "If you are very sure, type 'Yes I'm very sure!' to continue.")
if answer != "Yes I'm very sure!":
    print "Incorrect answer."
    sys.exit(1)

scl = j.clients.osis.getNamespace('system')
creds = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']

print ""

ip = j.console.askString("\nProvide the ip address of master of the storage backend")

cleanup([ip], creds['client_id'], creds['client_secret'])
