def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    gid = args.getTag('gid')
    if gid:
        filters['gid'] = int(gid)

    fieldnames = ['Name', 'Network', 'Netmask', 'GID', 'VLAN', 'Free']

    def getFreeIPS(row, id):
        return str(len(row[id]))

    fields = [
            {'name': 'Name',
             'id': 'name',
             'value': '[%(name)s|External Network?networkid=%(id)s]',
            },
            {'name': 'Network',
             'id': 'network',
             'value': 'network',
             'type': 'text',
            },
            {'name': 'Netmask',
             'id': 'subnetmask',
             'value': 'subnetmask',
             'type': 'text',
            },
            {'name': 'GID',
             'id': 'gid',
             'value': 'gid',
            },
            {'name': 'VLAN',
             'id': 'vlan',
             'value': 'vlan',
            },
            {'name': 'Free',
             'id': 'ips',
             'value': getFreeIPS,
             'sortable': False,
             'filterable': False,
            },
    ]
    tableid = modifier.addTableFromModel('cloudbroker', 'externalnetwork', fields, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
