
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    def get_ips(row, fields):
        return ', '.join(row['ipaddr'])

    fields = [
        {
            'name': 'Grid ID',
            'value': '[%(gid)s|/CBGrid/grid?id=%(gid)s]',
            'id': 'gid'
        }, {
            'name': 'Name',
            'value': '[%(name)s|/grid/Grid Node?id=%(id)s&gid=%(gid)s]',
            'id': 'name'
        }, {
            'name': 'Status',
            'value': 'active',
            'id': 'status'
        }, {
            'name': 'IP Address',
            'id': 'ipaddr',
            'value': get_ips
        }
    ]
    tableid = modifier.addTableFromModel('system', 'node', fields, selectable='rows', filters={'roles': 'storagedriver'})
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params

