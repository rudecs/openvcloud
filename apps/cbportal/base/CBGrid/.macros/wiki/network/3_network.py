try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    gid = args.getTag('gid')
    if not id or not gid:
        out = 'Missing network id param "id" or "gid"'
        params.result = (out, args.doc)
        return params

    id = int(id)
    vcl = j.clients.osis.getForNamespace('vfw')
    key = "%s_%s" % (gid, id)

    if not vcl.virtualfirewall.exists(key):
        params.result = ('Network with id %s not found' % key, args.doc)
        return params

    network =  vcl.virtualfirewall.get(key)
    obj = network.dump()
    obj['pubips'] = ', '.join(obj['pubips'])

    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
