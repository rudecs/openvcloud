
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    gid = args.getTag('gid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.clients.osis.getForCategory(j.core.portal.active.osis, 'cloudbroker', 'publicipv4pool')
    query = {}
    if gid:
        query['gid'] = int(gid)
    allips = list()
    [allips.extend(publicipv4pool['pubips']) for publicipv4pool in ac.search({})[1:]]
    total = len(allips)
    gridips = list()
    [gridips.extend(publicipv4pool['pubips']) for publicipv4pool in ac.search(query)[1:]]
    running = len(gridips)
    if running < 10:
        result += '\n{color:red}** *LESS THAN 10 FREE IPs*{color}'
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
