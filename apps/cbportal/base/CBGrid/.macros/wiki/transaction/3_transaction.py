
def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing credit transaction id param "id"'
        params.result = (out, args.doc)
        return params

    id = int(id)
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    if not cbclient.credittransaction.exists(id):
        params.result = ('credit transaction with id %s not found' % id, args.doc)
        return params

    credittransaction = cbclient.credittransaction.get(id)
    def objFetchManipulate(id):
        obj = credittransaction.dump()
        obj['time'] = j.base.time.epoch2HRDateTime(obj['time'])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
