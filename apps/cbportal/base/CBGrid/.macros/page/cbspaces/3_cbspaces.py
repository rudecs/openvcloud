
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    accountId = args.getTag('accountId')
    if accountId:
        filters['accountId'] = int(accountId)

    fieldnames = ['ID', 'Name', 'Account ID', 'Network ID', 'Stacks IDs', 'Location', 'Status', 'Public IP Address']

    def makeRPS(row, field):
        links = list()
        for rps in row[field]:
            links.append('[%s|/CBGrid/stack?id=%s]' % (rps, rps))
        return ', '.join(links)

    fieldids = ['id', 'name', 'accountId', 'networkId', 'resourceProviderStacks', 'location', 'status', 'publicipaddress']
    fieldvalues = ['[%(id)s|/CBGrid/cloudspace?id=%(id)s]', 'name', 
                   '[%(accountId)s|/CBGrid/account?id=%(accountId)s]', 
                   '[%(networkId)s|/CBGrid/network?id=%(networkId)s&gid=%(gid)s]', makeRPS, 'location', 'status', 
                   'publicipaddress']
    tableid = modifier.addTableForModel('cloudbroker', 'cloudspace', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
