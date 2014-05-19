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

    space = cbclient.cloudspace.get(id)
    if not space:
        params.result = ('CloudSpace with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = space.dump()
        
        resourceLimits = list()
        for k, v in obj['resourceLimits'].iteritems():
            resourceLimits.append('%s: %s'% (k, str(v)))
        obj['resourceLimits'] = str('<br>'.join(resourceLimits))
    
        links = list()
        for rps in obj['resourceProviderStacks']:
            links.append('[%s|CBGrid/stack?id=%s]' % (rps, rps))
        obj['resourceProviderStacks'] = ', '.join(links)

        obj['acl'] = str(', '.join(['%s:%s' % (acl['userGroupId'], acl['right']) for acl in obj['acl']]))

        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
