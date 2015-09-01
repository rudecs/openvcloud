def main(j, args, params, tags, tasklet):
    import netaddr

    id = args.getTag('networkid')
    if not id:
        out = 'Missing networkid param "id"'
        params.result = (out, args.doc)
        return params
    
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    if not cbclient.publicipv4pool.exists(id):
        params.result = ('Account with id %s not found' % id, args.doc)
        return params

    network = cbclient.publicipv4pool.get(id).dump()
    network['spaces'] = list()

    networkpool = netaddr.IPNetwork(network['id'])

    for space in cbclient.cloudspace.search({'$query': {'gid': network['gid'], 'status': 'DEPLOYED'}, '$fields': ['id', 'publicipaddress']})[1:]:
        if netaddr.IPNetwork(space['publicipaddress']).ip in networkpool:
            network['spaces'].append(space)

    args.doc.applyTemplate(network)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
