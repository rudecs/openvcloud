import datetime

def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.core.osis.getClientForCategory(j.core.portal.active.osis, 'cloudbroker', 'vmachine')
    total = ac.count({'status':{'$ne': 'DESTROYED'}})
    running = ac.count({'status': 'RUNNING'})
    result = result % {'height': height,
                       'width': width,
                       'running': running,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
