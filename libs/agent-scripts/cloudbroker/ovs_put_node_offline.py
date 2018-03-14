from JumpScale import j  # NOQA

descr = """
Put node offline on ovs
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
async = True


def action(interface='storage'):
    import json
    scl = j.clients.osis.getNamespace('system')
    ovs = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']
    ovscl = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))
    node = scl.node.get(j.application.whoAmI.nid)
    for netaddr in node.netaddr:
        if netaddr['name'] == interface:
            storageIP = netaddr['ip'][0]
            break
    else:
        raise RuntimeError('Storage Node does not have interface for storage ip , please specify storage interface')
    # get the storage router data 
    storage_router_query = dict(type='AND', items=[('ip', 'EQUALS', storageIP)])
    storage_router = ovscl.get('/storagerouters',
                               params=dict(contents='node_type,vpools_guids,storagedrivers,vdisks_guids', 
                                           query=json.dumps(storage_router_query)))['data'][0]

    output = ovscl.post('/storagerouters/{}/mark_offline/'.format(storage_router['guid']))
    if output.get('error'):
        raise RuntimeError(output.get('error_description'))
    return True
