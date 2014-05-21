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

    cbclient = j.core.osis.getClientForNamespace('cloudbroker')

    if not cbclient.network.exists(id):
        params.result = ('Network with id %s not found' % id, args.doc)
        return params

    network = cbclient.network.get(id)
    def objFetchManipulate(id):
        obj = network.dump()
        obj['nameservers'] = str(', '.join(obj['nameservers'])) or ' '
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
