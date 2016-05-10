def main(j, args, params, tags, tasklet):
    import netaddr
    import re

    params.result = (args.doc, args.doc)
    id = args.getTag('networkid')
    if not id and re.search('^\d+\.\d+\.\d+\.\d+/\d+$', id):
        args.doc.applyTemplate({})
        return params
    
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    if not cbclient.publicipv4pool.exists(id):
        args.doc.applyTemplate({id: None}, True)
        return params

    network = cbclient.publicipv4pool.get(id).dump()
    network['spaces'] = list()
    network['vms'] = list()

    networkpool = netaddr.IPNetwork(network['id'])

    for space in cbclient.cloudspace.search({'$query': {'gid': network['gid'], 'status': 'DEPLOYED'}, '$fields': ['id','name', 'publicipaddress']})[1:]:
        if netaddr.IPNetwork(space['publicipaddress']).ip in networkpool:
            network['spaces'].append(space)
    for vm in cbclient.vmachine.search({'nics.type': 'PUBLIC', 'status': {'$nin': ['ERROR', 'DESTROYED']}})[1:]:
        for nic in vm['nics']:
            if nic['type'] == 'PUBLIC' and netaddr.IPNetwork(nic['ipAddress']).ip in networkpool:
                vm['publicipaddress'] = nic['ipAddress']
                network['vms'].append(vm)

    args.doc.applyTemplate(network, True)
    return params

def match(j, args, params, tags, tasklet):
    return True
