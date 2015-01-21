
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    gid = args.getTag('gid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.core.osis.getClientForCategory(j.core.portal.active.osis, 'libcloud', 'libvirtdomain')
    key = 'networkids_%s' % gid
    if ac.exists(key):
        networkids = ac.get(key)
    else:
        networkids = []
    allkeys = ac.list()
    allnetworkids = list()
    [allnetworkids.extend(ac.get(key)) for key in allkeys if key.startswith('networkids_')]
    total = len(allnetworkids)
    running = len(networkids)
    if running < 10:
        result += '\n{color:red}** *LESS THAN 10 FREE NETWORK IDs*{color}'
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
