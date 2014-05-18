
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'Access Control List']

    def makeACL(row, field):
        return str('<br>'.join(['%s:%s' % (acl['userGroupId'], acl['right']) for acl in row[field]]))

    def makeLink(row, field):
        return '[%s|CBGrid/account?id=%s]' % (row[field], row[field])

    fieldids = ['id', 'name', 'acl']
    fieldvalues = [makeLink, 'name', makeACL]
    tableid = modifier.addTableForModel('cloudbroker', 'account', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
