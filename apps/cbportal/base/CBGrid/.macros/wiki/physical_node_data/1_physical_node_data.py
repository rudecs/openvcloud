
def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    nid = args.requestContext.params.get('id')
    gid = args.requestContext.params.get('gid')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    scl = j.clients.osis.getNamespace('system')
    node = scl.node.searchOne({'id': int(nid) if nid else None})
    data = {'node':None, 'stack': None, 'ovs': None}

    # check node exists
    if not node:
        args.doc.applyTemplate(data, True)
        return params
    data['node'] = node

    for netaddr in node['netaddr']:
        if netaddr['name'] == 'storage':
            data['storageip'] = netaddr['ip'][0]
            break
    else:
        args.doc.applyTemplate(data, True)
        return params

    # get stack data if stack exists and is cpunode
    if 'cpunode' in node['roles']:
        stack = ccl.stack.searchOne({'referenceId': nid})
        if not stack:
            args.doc.applyTemplate({'id': None, 'eco': 'Stack Id not Found'}, True)
            return params
        data['stack'] = stack

    if 'storagedriver' in node['roles']:
        acl = j.clients.agentcontroller.get()
        output = acl.executeJumpscript('greenitglobe', 'cloudbroker_get_storagenode', nid=nid, gid=gid, wait=True)
        if output['errorreport']or output['state'] == 'ERROR':
            args.doc.applyTemplate({'job': output['guid']})
            return params
        data['ovs'] = output['result']

    args.doc.applyTemplate(data)
    return params


def match(j, args, params, tags, tasklet):
    return True
