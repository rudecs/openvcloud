
def main(j, args, params, tags, tasklet):
    import json
    gid = args.getTag('gid')
    syscl = j.clients.osis.getNamespace('system')
    vcl = j.clients.osis.getNamespace('vfw')
    
    def _formatdata(fwdata):
        aaData = list()
        for name, nid, nr in fwdata:
            itemdata = ['<a href=/grid/grid node?id=%s>%s</a>' % (nid, name)]
            itemdata.append(str(nr))
            aaData.append(itemdata)
        return json.dumps(aaData)

    query = {'roles':'fw'}
    if gid:
        query['gid'] = int(gid)
    fwnodes = syscl.node.search(query)[1:]

    fwdata = list()
    for fwnode in fwnodes:
        nid = int(fwnode['id'])
        query = {'nid': nid, 'gid': fwnode['gid']}
        number = vcl.virtualfirewall.count(query)
        fwdata.append((fwnode['name'], nid, number))
    fwnodes = _formatdata(fwdata)

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ('Firewall Node', 'Number of firewalls deployed on it')
    tableid = modifier.addTableFromData(fwnodes, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
