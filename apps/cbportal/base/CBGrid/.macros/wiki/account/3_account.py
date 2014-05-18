try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing account id param "id"'
        params.result = (out, args.doc)
        return params

    import JumpScale.grid.osis
    cbclient = j.core.osis.getClientForNamespace('cloudbroker')

    account = cbclient.account.simpleSearch({'id':id})
    if not account:
        params.result = ('Account with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = account[0]
        obj['acl'] = str(', '.join(['*%s*:%s' % (acl['userGroupId'], acl['right']) for acl in obj['acl']]))

        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
