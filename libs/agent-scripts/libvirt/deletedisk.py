from JumpScale import j

descr = """
Libvirt script to delete a disk
"""

name = "deletedisk"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskguid):
    # Deletes a disk
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguid: guid of the disk to delete

    path = "/vdisks/{}".format(diskguid)

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    taskguid = ovs.delete(path)
    success, result = ovs.wait_for_task(taskguid)

    if success:
        return result
    else:
        raise Exception("Could not delete disk:\n{}".format(result))
