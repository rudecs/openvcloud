from JumpScale import j
import json


descr = """
Libvirt script to create a volume
"""

name = "createdisk"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, vpoolguid, storagerouterguid, diskname, size, pagecache_ratio):
    # Creates a new blank disk
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # vpoolguid: guid of the vpool on which we create the disk
    # storagerouterguid: guid of the storagerouter on wich we create the disk
    # diskname: name for the disk
    # size: size of the disk in GB
    # pagecache_ratio: amount of metadata the volumedriver should hold in memory cache
    #
    # returns diskguid of the created disk

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    nodekey = j.application.getAgentId()
    rcl = j.clients.redis.getByInstance('system')
    statsclient = j.tools.aggregator.getClient(rcl, nodekey)

    poolpath = "/vpools/{vpoolguid}".format(vpoolguid=vpoolguid)
    pool = ovs.get(poolpath)
    path = "/vdisks/"
    backend_name = pool['backend_info']['name']

    # backends
    free = sum([stat.val for stat in statsclient.statsByPrefix("ovs.backend.free@{backend_name}".format(backend_name=backend_name))])
    used = sum([stat.val for stat in statsclient.statsByPrefix("ovs.backend.used@{backend_name}".format(backend_name=backend_name))])

    total = free + used
    if (used * 100.0 / total) >= 80:
        raise Exception("Used capacity on {backend_name} >= 80%".format(backend_name=backend_name))

    data = dict(name=diskname, size=size * 1024**3, storagerouter_guid=storagerouterguid,
                vpool_guid=vpoolguid, pagecache_ratio=pagecache_ratio / 100.0)

    taskguid = ovs.post(path, data=json.dumps(data))
    success, result = ovs.wait_for_task(taskguid)

    if success:
        return result
    else:
        raise Exception("Could not create disk:\n{}".format(result))
