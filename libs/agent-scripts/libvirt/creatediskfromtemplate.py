from JumpScale import j
import json

descr = """
Libvirt script to create a disk from a disk template
"""

name = "creatediskfromtemplate"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, storagerouterguid, diskname, size, templateguid):
    # Creates a disk from a disk template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # storagerouterguid: guid of the storagerouter on wich we create the disk
    # diskname: name for the disk
    # size: size of the disk in GB
    # templateguid: guid of the template that needs to be used to create
    #   the volume. If omitted a blank vdisk is created.

    # returns diskguid of the created disk

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    # First create the disk
    path = "/vdisks/{}/create_from_template".format(templateguid)
    params = dict(name=diskname, storagerouter_guid=storagerouterguid)
    taskguid = ovs.post(path, params=params)
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not create disk:\n{}".format(result))

    diskguid = result['vdisk_guid']

    # Then resize to the correct size
    path = "/vdisks/{}/extend".format(diskguid)
    params = dict(new_size=size * 1000**3)
    #taskguid = ovs.post(path, data=json.dumps(params))
    #success, result = ovs.wait_for_task(taskguid)

    #if not success:
        #raise Exception("Could not create disk:\n{}".format(result))

    return diskguid
