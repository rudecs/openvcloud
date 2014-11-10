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

    oscl = j.core.osis.getClientByInstance('main')
    userclient = j.core.osis.getClientForCategory(oscl, 'system', 'user')

    if not userclient.exists(id):
        params.result = ('User with id %s not found' % id, args.doc)
        return params

    user = userclient.get(id)
   
    obj = user.dump()
    obj['lastcheck'] = j.base.time.epoch2HRDateTime(obj['lastcheck']) if obj['lastcheck'] else 'Never'

    for attr in ['roles', 'groups']:
        obj[attr] = ', '.join(obj[attr])

    obj['passwd'] = unicode(obj['passwd'], errors='ignore')
    authkey = user.authkey
    if user.authkey:
        session = args.requestContext.env['beaker.session']
        if session.get_by_id(session):
            authkey = None
    if not authkey:
        newsession = args.requestContext.env['beaker.get_session']()
        newsession['user'] = user.id
        newsession['account_status'] = 'CONFIRMED'
        newsession.save()
        authkey = user.authkey = newsession.id
        userclient.set(user)
    portalurl = j.apps.cloudbroker.iaas.cb.actors.cloudapi.locations.getUrl()
    obj['loginurl'] = "%s/wiki_gcb/login?username=%s&apiKey=%s" % (portalurl, user.id, authkey)

    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
