def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    gid = args.getTag('gid')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    vmcl = j.clients.osis.getForCategory(j.core.portal.active.osis, 'cloudbroker', 'vmachine')
    stackcl = j.clients.osis.getForCategory(j.core.portal.active.osis, 'cloudbroker', 'stack')
    imgcl = j.clients.osis.getForCategory(j.core.portal.active.osis, 'cloudbroker', 'image')
    images = [ x['id'] for x in imgcl.search({'type':'Windows'})[1:] ]
    query = {'status': 'RUNNING', 'imageId': {'$in': images}}
    if gid:
	stacks = [ stack['id'] for stack in stackcl.search({'gid': int(gid)})[1:] ]
	query['stackId'] = {'$in': stacks}
    active = vmcl.count(query) 
    total = vmcl.count({'status':{'$ne': 'DESTROYED'}})
    result = result % {'height': height,
                       'width': width,
                       'running': active,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True

