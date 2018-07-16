def main(j, args, params, tags, tasklet):
    from cloudbrokerlib import resourcestatus
    import cgi
    page = args.page
    page.addJS('/system/.files/js/action.js', header=False)
    modifier = j.html.getPageModifierGridDataTables(page)
    filters = {'status': resourcestatus.Cloudspace.DELETED}

    def nameLinkify(row, field):
        val = row[field]
        if not isinstance(row[field], int):
            val = cgi.escape(row[field])
        return '[%s|Cloud Space?id=%s]' % (val, row['id'])

    def remove_icon(row, field):
        tags = {"data-cloudspaceId": row[field]}
        return page.getActionHtml('action-DestroyCloudspace', tags, 'glyphicon glyphicon-remove')

    def restore_icon(row, field):
        tags = {"data-cloudspaceId": row[field]}
        return page.getActionHtml('action-RestoreCloudspace', tags, 'glyphicon glyphicon-repeat')

    fields = [
        {
            'name': 'ID',
            'value': nameLinkify,
            'id': 'id',
        }, {
            'name': 'Name',
            'value': nameLinkify,
            'id': 'name',
        }, {
            'name': 'Destroy',
            'value': remove_icon,
            'id': 'id',
        }, {
            'name': 'Restore',
            'value': restore_icon,
            'id': 'id'
        }
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'cloudspace', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params