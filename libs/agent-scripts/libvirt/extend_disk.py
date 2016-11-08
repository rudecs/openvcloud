from JumpScale import j
import json

descr = """
Libvirt script to extend a disksize on ovs
"""

category = "libvirt"
organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, size, diskguid):
    # Creates a disk from a disk template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # size: size of the disk in GB
    # diskguid: guid of the disk that needs to be used to update
    #   the volume.

    # returns diskguid of the adjusted disk

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    # Then resize to the correct size
    path = "/vdisks/{}/extend".format(diskguid)
    params = dict(new_size=size * 1024**3)
    taskguid = ovs.post(path, data=json.dumps(params))
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not update disk:\n{}".format(result))

    return diskguid
