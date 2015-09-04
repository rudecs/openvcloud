def main(j, args, params, tags, tasklet):
    guid = args.getTag('guid')
    if not guid:
        out = 'Missing GUID'
        params.result = (out, args.doc)
        return params

    user = j.apps.system.usermanager.modelUser.get(guid)
    if not user:
        out = 'Could not find Username: %s' % guid
        params.result = (out, args.doc)
        return params

    authkey = user.authkey
    if user.authkey:
        # validate if authkey is still valid
        session = args.requestContext.env['beaker.session']
        if not session.get_by_id(user.authkey):
            authkey = None
    if not authkey:
        newsession = args.requestContext.env['beaker.get_session']()
        newsession['user'] = user.id
        newsession['account_status'] = 'CONFIRMED'
        newsession.save()
        authkey = user.authkey = newsession.id
        j.apps.system.usermanager.modelUser.set(user)
    portalurl = j.apps.cloudbroker.iaas.cb.actors.cloudapi.locations.getUrl()

    obj = user.dump()
    obj['loginurl'] = "%s/wiki_gcb/login#?username=%s&apiKey=%s" % (portalurl, user.id, authkey)

    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params
