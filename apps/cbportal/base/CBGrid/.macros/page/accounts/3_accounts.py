
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()

    userGroupId = args.getTag('acl.userGroupId')
    if userGroupId:
        filters['acl.userGroupId'] = userGroupId


    fieldnames = ['ID', 'Name', 'Status', 'Access Control List']

    def makeACL(row, field):
        return str('<br>'.join(['%s:%s' % (acl['userGroupId'], acl['right']) for acl in row[field]]))

    fieldids = ['id', 'name', 'status', 'acl']
    fieldvalues = ['[%(id)s|/CBGrid/account?id=%(id)s]', 'name', 'status', makeACL]
    tableid = modifier.addTableForModel('cloudbroker', 'account', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
