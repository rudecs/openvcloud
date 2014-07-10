try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing network id param "id"'
        params.result = (out, args.doc)
        return params

    vcl = j.core.osis.getClientForNamespace('vfw')
    key = "%s_%s" % (j.application.whoAmI.gid, id)

    if not vcl.virtualfirewall.exists(key):
        params.result = ('Network with id %s not found' % id, args.doc)
        return params

    network =  vcl.virtualfirewall.get(key)
    obj = network.dump()
    obj['pubips'] = ', '.join(obj['pubips'])

    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
