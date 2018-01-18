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
            _, ip = j.apps.cloudbroker.zeroaccess._get_node_info(node_id)
            if not ip:
                continue

        name = '<a href="/cbgrid/0-access Node?node={id}">{name}</a>'.format(name=node.name, id=node_id)
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
