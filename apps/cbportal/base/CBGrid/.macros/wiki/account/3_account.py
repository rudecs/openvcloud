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

    cbclient = j.core.osis.getClientForNamespace('cloudbroker')

    accountobj = cbclient.account.get(id)
    if not accountobj:
        params.result = ('Account with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        account = accountobj.dump()
        account['acl'] = str(', '.join([' *%s*:%s' % (acl['userGroupId'], acl['right']) for acl in account['acl']]))

        return account

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
