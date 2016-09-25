def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    gid = args.getTag('gid')
    if gid:
        filters['gid'] = int(gid)

    fieldnames = ['Network', 'GID', 'Netmask', 'Free']

    def getFreeIPS(row, id):
        return str(len(row[id]))

    fieldids = ['id', 'gid', 'netmask', 'pubips']
    fieldvalues = ['[%(id)s|public network?networkid=%(id)s]', 'gid', 'subnetmask', getFreeIPS]
    tableid = modifier.addTableForModel('cloudbroker', 'publicipv4pool', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True