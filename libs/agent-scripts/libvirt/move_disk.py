from JumpScale import j
import json

descr = """
Libvirt script to move disk from storagerouter
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, storagerouterguid, diskguid=None, devicename=None):
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

    if not diskguid:
        # First query for the diskguid
        query = dict(type='AND', items=[('devicename', 'EQUALS', devicename)])
        result = ovs.get('/vdisks', params=dict(contents='name,devicename', query=json.dumps(query)))
        disksfound = len(result['data'])
        if disksfound == 0:
            return False
        elif disksfound > 1:
            raise Exception('More than 1 disk found. Do not know what to do.')

        diskguid = result['data'][0]['guid']

    # Then resize to the correct size
    path = "/vdisks/{}/move".format(diskguid)
    params = dict(target_storagerouter_guid=storagerouterguid)
    taskguid = ovs.post(path, params=params)
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not update disk:\n{}".format(result))

    return diskguid
