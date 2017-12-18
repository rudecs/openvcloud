from JumpScale import j
import time

descr = """
Create a snapshot of a number of disks
"""

name = "createsnapshots"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskguids, name):
    # Create a snapshot with name name on each disk
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguids: array of guids of the disks to delete
    # name: name for the snapshot
    #
    # returns None
    snapshots = {}

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    path = '/vdisks/{}/create_snapshot'
    params = dict(name=name, sticky=True)

    for diskguid in diskguids:
        taskguid = ovs.post(path.format(diskguid), params=params)
        success, result = ovs.wait_for_task(taskguid)
        if not success:
            raise Exception("Could not create snapshots:\n{}".format(result))
        snapshots[diskguid] = result
    return snapshots
