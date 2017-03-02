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


def action(ovs_connection, storagerouterguid, diskname, size, templateguid, pagecache_ratio):
    # Creates a disk from a disk template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # storagerouterguid: guid of the storagerouter on wich we create the disk
    # diskname: name for the disk
    # size: size of the disk in GB
    # templateguid: guid of the template that needs to be used to create
    #   the volume. If omitted a blank vdisk is created.
    # pagecache_ratio: amount of metadata the volumedriver should hold in memory cache

    # returns diskguid of the created disk

    path = "/vdisks/"
    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    nodekey = j.application.getAgentId()
    rcl = j.clients.redis.getByInstance('system')
    statsclient = j.tools.aggregator.getClient(rcl, nodekey)

    diskpath = "/vdisks/{templateguid}".format(templateguid=templateguid)
    disk = ovs.get(diskpath)

    vpoolguid = disk['vpool_guid']

    poolpath = "/vpools/{vpoolguid}".format(vpoolguid=vpoolguid)
    pool = ovs.get(poolpath)
    backend_name = pool['backend_info']['name']

    # backends
    free = sum([stat.val for stat in statsclient.statsByPrefix("ovs.backend.free@{backend_name}".format(backend_name=backend_name))])
    used = sum([stat.val for stat in statsclient.statsByPrefix("ovs.backend.used@{backend_name}".format(backend_name=backend_name))])

    total = free + used
    if (used * 100.0 / total) >= 80:
        raise Exception("Used capacity on {backend_name} >= 80%".format(backend_name=backend_name))
    # First create the disk
    path = "/vdisks/{}/create_from_template".format(templateguid)
    params = dict(name=diskname, storagerouter_guid=storagerouterguid,
                  pagecache_ratio=pagecache_ratio / 100.0)
    taskguid = ovs.post(path, params=params)
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not create disk:\n{}".format(result))

    diskguid = result['vdisk_guid']

    # Then resize to the correct size
    path = "/vdisks/{}/extend".format(diskguid)
    params = dict(new_size=size * 1024**3)
    taskguid = ovs.post(path, data=json.dumps(params))
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not create disk:\n{}".format(result))

    return diskguid
