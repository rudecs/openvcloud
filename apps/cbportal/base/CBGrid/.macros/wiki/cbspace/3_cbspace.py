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

    id = int(id)
    cbclient = j.core.osis.getClientForNamespace('cloudbroker')
    vcl = j.core.osis.getClientForNamespace('vfw')

    if not cbclient.cloudspace.exists(id):
        params.result = ('CloudSpace with id %s not found' % id, args.doc)
        return params

    space = cbclient.cloudspace.get(id)

    obj = space.dump()
    
    accountid = obj['accountId']
    account = cbclient.account.get(accountid).dump() if cbclient.account.exists(accountid) else {'name':'N/A'}
    obj['accountname'] = account['name']

    resourceLimits = list()
    for k, v in obj['resourceLimits'].iteritems():
        resourceLimits.append(' *%s*: %s'% (k, str(v)))
    obj['resourceLimits'] = str(', '.join(resourceLimits))

    obj['acl'] = str(', '.join([' *%s*:%s' % (acl['userGroupId'], acl['right']) for acl in obj['acl']]))

    vfwkey = "%(gid)s_%(networkId)s" % (obj)
    if vcl.virtualfirewall.exists(vfwkey):
        network =  vcl.virtualfirewall.get(vfwkey).dump()
        obj['networkid'] = '[%s|network?id=%s&gid=%s]' % (obj['networkId'], obj['networkId'], obj['gid'])
        obj['network'] = network
    else:
        if obj['networkId']:
            obj['networkid'] = obj['networkId']
        else:
            obj['networkid'] = 'N/A'
        obj['network'] = {'tcpForwardRules': []}


    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
