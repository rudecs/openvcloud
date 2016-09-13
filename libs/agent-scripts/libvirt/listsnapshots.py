from JumpScale import j
import itertools
import gevent

descr = """
List snapshots of a specific machine
"""

name = "listsnapshots"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskguids):
    # Lists snapshots
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguids: array of guids of the disks to delete
    #
    # returns list of dicts with name snapshot combinations
    #  eg: [{'name': 'ultimate', 'timestamp': 1368774635484}, ...]

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    path = '/vdisks/{}'

    jobs = [gevent.spawn(ovs.get, path.format(diskguid)) for diskguid in diskguids]
    gevent.joinall(jobs)
    snapshots = set()
    for snapshot in itertools.chain((job.value['snapshots'] for job in jobs)):
        if snapshot['is_automatic']:
            continue
        snapshots.add((snapshot['name'], int(snapshot['timestamp'])))

    return [dict(name=snapshot[0], timestamp=snapshot[1]) for snapshot in snapshots]
