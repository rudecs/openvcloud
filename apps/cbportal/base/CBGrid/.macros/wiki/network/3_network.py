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

    import JumpScale.grid.osis
    cbclient = j.core.osis.getClientForNamespace('cloudbroker')

    network = cbclient.network.simpleSearch({'id':id})
    if not network:
        params.result = ('Network with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = network[0]
        obj['nameservers'] = str(', '.join(obj['nameservers'])) or ' '
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
