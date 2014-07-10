
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'CloudSpace', 'Public IPs', 'Management IP' ]

    def makeNS(row, field):
        return str(', '.join(row[field]))

    fieldids = ['id', 'domain', 'pubips', 'host']
    fieldvalues = ['[%(id)s|/CBGrid/network?id=%(id)s]',
                   '[%(domain)s|/CBGrid/cloudspace?id=%(domain)s]',
                   makeNS,
                   'host'
                   ]
    tableid = modifier.addTableForModel('vfw', 'virtualfirewall', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
