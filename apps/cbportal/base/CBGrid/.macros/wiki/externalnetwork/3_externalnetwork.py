def main(j, args, params, tags, tasklet):

    params.result = (args.doc, args.doc)
    networkid = args.getTag('networkid')
    if not networkid:
        args.doc.applyTemplate({})
        return params

    cbclient = j.clients.osis.getNamespace('cloudbroker')
    networkid = int(networkid)

    if not cbclient.externalnetwork.exists(networkid):
        args.doc.applyTemplate({id: None}, True)
        return params

    pool = cbclient.externalnetwork.get(networkid)
    networkinfo = j.apps.cloudbroker.iaas.getUsedIPInfo(pool)
    network = pool.dump()
    network.update(networkinfo)

    args.doc.applyTemplate(network, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
