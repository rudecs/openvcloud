def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    ocl = j.clients.osis.getNamespace('system')
    nodes = []
    for node_id in ocl.node.list():
        node = ocl.node.get(node_id)
        ip = ""
        if 'master' in node.roles:
            continue
        else:
            for addr in node.netaddr:
                if addr['name'] == "backplane1":
                    ip = addr['ip'][0]
                    break
            else:
                continue

        name = '<a href="/cbgrid/0-access Node?node={name}&ip={ip}">{name}</a>'.format(name=node.name, ip=ip)
        nodes.append([node.id, name, ip])

    fieldnames = ['ID', 'Name', 'IP']
    if nodes:
        page.addList(nodes, fieldnames)
    else:
        page.addList([['Can not list nodes', '', '']], fieldnames)
   
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
