def main(j, args, params, tags, tasklet):
    from jose import jwt as jose_jwt
    from JumpScale.portal.portal import exceptions
    import json
    params.result = (args.doc, args.doc)
    node_id = args.requestContext.params.get('node')
    remote = None
    data =  {}
    if node_id:
        node_name, remote = j.apps.cloudbroker.zeroaccess._get_node_info(node_id)
        data['name'] = node_name
    oauth = j.clients.oauth.get(instance='itsyouonline')
    try:
        jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    except:
        raise exceptions.NotFound('Page not found')
    if jwt:
        jwt_data = jose_jwt.get_unverified_claims(jwt)
        jwt_data = json.loads(jwt_data)
        scope = "user:memberof:{}.0-access".format(oauth.id)
        if scope not in jwt_data['scope']:
            raise exceptions.NotFound('Page not found')
        table_data = j.apps.cloudbroker.zeroaccess.listSessions(remote=remote, ctx=args.requestContext)
    else:
        table_data = [['No jwt found please logout and login again', '', '', '', '']]

    if not table_data:
        table_data = [['No sessions found', '', '', '', '']]
    
    data['tables'] = table_data
    args.doc.applyTemplate(data, False)
    return params


def match(j, args, params, tags, tasklet):
    return True
