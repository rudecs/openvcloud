
def main(j, args, params, tags, tasklet):
    gid = args.getTag('gid')
    syscl = j.core.osis.getClientForNamespace('system')
    vcl = j.core.osis.getClientForNamespace('vfw')
    
    def _formatdata(fwdata):
        aaData = list()
        for name, nid, nr in fwdata:
            itemdata = ['<a href=/grid/node?id=%s>%s</a>' % (nid, name)]
            itemdata.append(str(nr))
            aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    query = {'roles':{'$in':['fw']}}
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
