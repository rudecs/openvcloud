from JumpScale import j
import urlparse
import json

descr = """
Libvirt script to delete a disk
"""

category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskpath):
    # Deletes every disk in diskguids
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskpath: edge client connection string
    #   eg: openvstorage+tcp://edgeclientip:port/routeros/0cc/routeros-small-0cc.raw
    #
    # returns None

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    pr = urlparse.urlparse(diskpath)
    devicename = pr.path

    # First query for the diskguid
    query = dict(type='AND', items=[('devicename', 'EQUALS', devicename)])
    result = ovs.get('/vdisks', params=dict(contents='name', query=json.dumps(query)))
    disksfound = len(result['data'])
    if disksfound == 0:
        return
    elif disksfound > 1:
        raise Exception('More than 1 disk found. Do not know what to do.')

    # Then delete the disk
    diskguid = result['data'][0]['guid']
    taskguid = ovs.delete("/vdisks/{}".format(diskguid))
    success, result = ovs.wait_for_task(taskguid)
    if not success:
        raise Exception("Could not delete disk:\n{}".format(result))

    return
