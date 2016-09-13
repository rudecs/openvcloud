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


def action(ovs_connection, vpoolguid, storagerouterguid, diskname, size):
    # Creates a new blank disk
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # vpoolguid: guid of the vpool on which we create the disk
    # storagerouterguid: guid of the storagerouter on wich we create the disk
    # diskname: name for the disk
    # size: size of the disk in GB
    #
    # returns diskguid of the created disk

    path = "/vdisks/"
    data = dict(name=diskname, size=size * 1000**3, storagerouter_guid=storagerouterguid,
                vpool_guid=vpoolguid)

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    taskguid = ovs.post(path, data=json.dumps(data))
    success, result = ovs.wait_for_task(taskguid)

    if success:
        return result
    else:
        raise Exception("Could not create disk:\n{}".format(result))
