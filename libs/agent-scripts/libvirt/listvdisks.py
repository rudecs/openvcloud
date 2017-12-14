from JumpScale import j

descr = """
Libvirt script to list vdisks
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, storagerouterguid):
    import json
    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                     ovs_connection['client_secret']))

    # First create a vpools dict
    query = {"type": "AND", "items":[["is_vtemplate", "EQUALS", False]]}
    result = ovs.get('/vdisks', params={'storagerouterguid': storagerouterguid, 'query': json.dumps(query)})
    return result['data']


if __name__ == '__main__':
    import pprint
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--storagerouterguid', help='Storagerouterguid')
    options = parser.parse_args()
    scl = j.clients.osis.getNamespace('system')
    grid = scl.grid.get(j.application.whoAmI.gid)
    credentials = grid.settings['ovs_credentials']
    credentials['ips'] = ['localhost']
    pprint.pprint(action(credentials, options.storagerouterguid))
