def main(j, args, params, tags, tasklet):
    from cloudbrokerlib import resourcestatus
    import cgi
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    disktype = args.getTag('type')
    filters = {'status': resourcestatus.Disk.TOBEDELETED, 'type': disktype}

    def nameLinkify(row, field):
        val = row[field]
        if not isinstance(row[field], int):
            val = cgi.escape(row[field])
        return '[%s|disk?id=%s]' % (val, row['id'])

    def remove_icon(row, field):
        tags = {"data-diskId": row[field]}
        return page.getActionHtml('action-DestroyDisk', tags, 'glyphicon glyphicon-remove')

    def restore_icon(row, field):
        tags = {"data-diskId": row[field]}
        return page.getActionHtml('action-RestoreDisk', tags, 'glyphicon glyphicon-repeat')

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
    if disktype == "C":
        tableid = "table_cdrom"
    else:
        tableid=None
    tableid = modifier.addTableFromModel('cloudbroker', 'disk', fields, filters, selectable='rows', tableid=tableid)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params