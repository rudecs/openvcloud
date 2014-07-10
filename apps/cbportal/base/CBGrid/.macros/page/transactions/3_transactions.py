
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    fieldids = ['id', 'accountId', 'amount', 'currency', 'status', 'time', 'comment']
    for tag, val in args.tags.tags.iteritems():
        if tag in fieldids:
            val = args.getTag(tag)
            filters[tag] = val

    #[u'comment', u'status', u'reference', u'currency', u'credit', u'amount', u'time', u'guid', u'id', u'accountId']
    fieldnames = ['ID', 'Account ID', 'Amount', 'Currency', 'Status', 'Transaction Time', 'Comment']

    fieldvalues = ['[%(id)s|/CBGrid/transaction?id=%(id)s]', 
                   '[%(accountId)s|/CBGrid/account?id=%(accountId)s]', 'amount', 'currency', 
                   'status', modifier.makeTime, 'comment']
    tableid = modifier.addTableForModel('cloudbroker', 'credittransaction', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
