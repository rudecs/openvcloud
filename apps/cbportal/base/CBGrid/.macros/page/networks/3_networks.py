import ujson as json

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['GID', 'ID', 'Cloud Space', 'Public IPs', 'Management IP' ]

    
    def _formatData():
        res = list()
        vfwcl = j.clients.osis.getNamespace('vfw')
        cbcl = j.clients.osis.getNamespace('cloudbroker')
        for fwid in vfwcl.virtualfirewall.list():
            fw = vfwcl.virtualfirewall.get(fwid)
            id = '<a href="/CBGrid/network?id=%s&gid=%s">%s</a> (%04x)' % (fw.id, fw.gid, fw.id, fw.id)
            cloudspace = cbcl.cloudspace.get(int(fw.domain))
            domain = '<a href="/CBGrid/cloudspace?id=%s">%s &nbsp; &nbsp; [%s] </a>' % (fw.domain, cloudspace.name, fw.domain)
            ns = ', '.join(fw.pubips)
            res.append([fw.gid, id, domain, ns, fw.host])
        return json.dumps(res)
    
    fieldvalues = _formatData()
    tableid = modifier.addTableFromData(fieldvalues, fieldnames)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
