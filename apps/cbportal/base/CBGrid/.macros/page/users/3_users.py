import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fieldnames = ['ID', 'Domain', 'Roles', 'Groups', 'Description', 'Active', 'Last Checked']

    def makeTime(row, field):
        return datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''

    def makeLink(row, field):
        return '[%s|CBGrid/user?id=%s]' % (row[field], row[field])

    fieldids = ['id', 'domain', 'roles', 'groups', 'description', 'active', 'lastcheck']
    fieldvalues = [makeLink, 'domain', 'roles', 'groups', 'description', 'active', makeTime]
    tableid = modifier.addTableForModel('system', 'user', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
