try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing user id param "id"'
        params.result = (out, args.doc)
        return params

    import JumpScale.grid.osis
    oscl = j.core.osis.getClient(user='root')
    userclient = j.core.osis.getClientForCategory(oscl, 'system', 'user')

    user = userclient.simpleSearch({'id':id})
    if not user:
        params.result = ('User with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        #u'domain', u'description', u'roles', u'emails', u'authkey', u'lastcheck', u'gid', u'groups', u'active', u'guid', u'id'
        obj = user[0]
        obj['lastcheck'] = j.base.time.epoch2HRDateTime(obj['lastcheck']) if obj['lastcheck'] else 'Never'

        for attr in ['roles', 'groups']:
            obj[attr] = ', '.join(obj[attr])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
