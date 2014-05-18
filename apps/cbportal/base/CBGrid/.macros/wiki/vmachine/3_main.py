import datetime
import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing VMachine ID param "id"'
        params.result = (out, args.doc)
        return params

    osiscl = j.core.osis.getClient(user='root')
    vmcl = j.core.osis.getClientForCategory(osiscl, 'cloudbroker', 'vmachine')
    try:
        obj = vmcl.get(id).__dict__
    except:
        out = 'Could not find VMachine Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    def objFetchManipulate(id):
        return obj

    push2doc = j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)
