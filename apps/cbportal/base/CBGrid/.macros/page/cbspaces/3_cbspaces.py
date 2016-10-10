def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    accountId = args.getTag('accountId')
    if accountId:
        filters['accountId'] = int(accountId)

    fieldnames = ['ID', 'Name', 'Account ID', 'Network ID', 'Location Code', 'Status', 'Public IP Address']

    def makeNetworkLink(row, field):
        if row[field]:
            return '[%(networkId)s|/CBGrid/private network?id=%(networkId)s&gid=%(gid)s]' % row
        else:
            return ''

    fieldids = ['id', 'name', 'accountId', 'networkId', 'location', 'status', 'publicipaddress']
    fieldvalues = ['[%(id)s|/CBGrid/Cloud Space?id=%(id)s]', 'name',
                   '[%(accountId)s|/CBGrid/account?id=%(accountId)s]',
                   makeNetworkLink, 'location', 'status',
                   'publicipaddress']
    tableid = modifier.addTableForModel('cloudbroker', 'cloudspace', fieldids, fieldnames, fieldvalues, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
