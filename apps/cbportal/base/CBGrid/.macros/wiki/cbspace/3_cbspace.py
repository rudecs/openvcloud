try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing CloudSpace id param "id"'
        params.result = (out, args.doc)
        return params

    cbclient = j.core.osis.getClientForNamespace('cloudbroker')

    if not cbclient.cloudspace.exists(id):
        params.result = ('CloudSpace with id %s not found' % id, args.doc)
        return params

    space = cbclient.cloudspace.get(id)

    def objFetchManipulate(id):
        obj = space.dump()
        
        accountid = obj['accountId']
        account = cbclient.account.get(accountid).dump() if cbclient.account.exists(accountid) else {'name':'N/A'}
        obj['accountname'] = account['name']

        resourceLimits = list()
        for k, v in obj['resourceLimits'].iteritems():
            resourceLimits.append(' *%s*: %s'% (k, str(v)))
        obj['resourceLimits'] = str(', '.join(resourceLimits))
    
        links = list()
        for rps in set(obj['resourceProviderStacks']):
            stack = cbclient.stack.get(rps).dump() if cbclient.stack.exists(rps) else {'name':'N/A'}
            links.append('[%s|CBGrid/stack?id=%s]' % (stack['name'], rps))
        obj['resourceProviderStacks'] = ', '.join(links)

        obj['acl'] = str(', '.join([' *%s*:%s' % (acl['userGroupId'], acl['right']) for acl in obj['acl']]))

        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
