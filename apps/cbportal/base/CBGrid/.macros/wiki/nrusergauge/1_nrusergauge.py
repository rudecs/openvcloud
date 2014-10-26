import datetime

def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    ac = j.core.osis.getClientForCategory(j.core.portal.active.osis, 'system', 'user')
    total = ac.count()
    active = ac.count({'active': True})
    result = result % {'height': height,
                       'width': width,
                       'running': active,
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
