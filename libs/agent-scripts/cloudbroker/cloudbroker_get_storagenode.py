from JumpScale import j  # NOQA

descr = """
Put node offline on ovs
"""

category = "cloudbroker"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
async = True


def action(interface='storage'):
    import json
    node_data = dict(storage_drivers={})
    scl = j.clients.osis.getNamespace('system')
    ovs = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']
    ovscl = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))
    node = scl.node.get( j.application.whoAmI.nid)
    for netaddr in node.netaddr:
        if netaddr['name'] == interface:
            node_data['ip'] = netaddr['ip'][0]
            break
    else:
        raise RuntimeError('Storage Node does not have interface for storage ip , please specify storage interface')
    # get the storage router data 
    storage_router_query = dict(type='AND', items=[('ip', 'EQUALS', node_data['ip'])])
    storage_router = ovscl.get('/storagerouters',
                               params=dict(contents='node_type,vpools_guids,storagedrivers,vdisks_guids', 
                                           query=json.dumps(storage_router_query)))['data'][0]

    node_data['vdisks_count'] = len(storage_router['vdisks_guids'])
    node_data['node_type'] = storage_router['node_type']
    
    # get the vpools , guids and data
    vpools_query = dict(type='OR', items=[])
    for vpool_guid in storage_router['vpools_guids']:
        vpools_query['items'].append(('guid', 'EQUALS', vpool_guid))
    vpools = ovscl.get('/vpools', params=dict(contents='name,_relations',
                                              query=json.dumps(vpools_query)))['data']
        
    
    # get the vpools , guids and data
    storage_driver_query = dict(type='OR', items=[])
    for storage_driver_guid in storage_router['storagedrivers_guids']:
        storage_driver_query['items'].append(('guid', 'EQUALS', storage_driver_guid))
    storage_drivers = ovscl.get('/storagedrivers', params=dict(contents='name,guid,ports', 
                                                                query=json.dumps(storage_driver_query)))['data']
    
    for vpool in vpools:
        for storage_driver in storage_drivers:
            if storage_driver['guid'] in vpool['storagedrivers_guids']:
                node_data['storage_drivers'][vpool['name']] = {'ports': storage_driver['ports']}
    return node_data


if __name__ == "__main__":
    print action()
    