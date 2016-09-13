from JumpScale import j
import time
import gevent

descr = """
Libvirt script to clone volumes
"""

name = "clonedisks"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True
queue = 'hypervisor'


def action(ovs_connection, diskguids, name, storagerouterguids):
    # Create a clone with name name for each disk
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguids: array of guids of the disks to delete
    # name: name for the clone
    # storagerouterguids: list of storage routers equaly sized as list of diskguids
    #
    # returns list of diskguids of cloned disks corresponding to the diskguids parameter

    if len(diskguids) != len(storagerouterguids):
        raise ValueError("Invalid input parameters")

    timestamp = int(time.time())
    snapshot_name = 'for clone {}'.format(name)
    snapshot_path = '/vdisks/{}/create_snapshot'
    clone_path = '/vdisks/{}/clone'
    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    def clone(diskguid, storagerouterguid):
        # First create snapshot
        params = dict(name=snapshot_name, timestamp=timestamp, sticky=True)
        taskguid = ovs.post(snapshot_path.format(diskguid), params=params)
        success, result = ovs.wait_for_task(taskguid)
        if not success:
            raise Exception("Could not create snapshot:\n{}".format(result))
        snapshot_guid = result

        # Create clone
        taskguid = ovs.post(clone_path.format(diskguid),
                            params=dict(name=name,
                                        storagerouter_guid=storagerouterguid,
                                        snapshot_id=snapshot_guid))
        success, result = ovs.wait_for_task(taskguid)
        if not success:
            raise Exception("Could not create snapshot:\n{}".format(result))
        return result['vdisk_guid']

    jobs = [gevent.spawn(clone, dg, sg) for dg, sg in zip(diskguids, storagerouterguids)]
    gevent.joinall(jobs)
    return [job.value for job in jobs]
