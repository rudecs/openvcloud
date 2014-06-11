
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    fieldids = ['id', 'accountId', 'credit', 'time']
    for tag, val in args.tags.tags.iteritems():
        if tag in fieldids:
            val = args.getTag(tag)
            filters[tag] = val

    fieldnames = ['ID', 'Account ID', 'Credit', 'Transaction Time']

    fieldvalues = ['id', '[%(accountId)s|/CBGrid/account?id=%(accountId)s]', 'credit', 
                   modifier.makeTime]
    tableid = modifier.addTableForModel('cloudbroker', 'creditbalance', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
