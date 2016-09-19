
def main(j, args, params, tags, tasklet):
    page = args.page
    storagenodedict = dict()

    scl = j.clients.osis.getNamespace('system')
    nodes = scl.node.search({"roles": "storagedriver"})[1:]
    for idx, node in enumerate(nodes):
        for nic in node["netaddr"]:
            if nic["name"] == "backplane1":
                node['publicip'] = nic["ip"][0]
                nodes[idx] = node


    storagenodedict['nodes'] = nodes



    args.doc.applyTemplate(cloudspacedict, True)
    return params


def match(j, args, params, tags, tasklet):
    return True
