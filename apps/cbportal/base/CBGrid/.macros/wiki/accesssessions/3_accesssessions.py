def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    node_id = args.requestContext.params.get('node')
    remote = None
    data =  {}
    if node_id:
        node_name, remote = j.apps.cloudbroker.zeroaccess._get_node_info(node_id)
        data['name'] = node_name
    oauth = j.clients.oauth.get(instance='itsyouonline')
    jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    if jwt:
        table_data = j.apps.cloudbroker.zeroaccess.listSessions(remote=remote, ctx=args.requestContext)
    else:
        table_data = [['No jwt found please login and out', '', '', '', '']]

    if not table_data:
        table_data = [['No sessions found', '', '', '', '']]
    
    data['tables'] = table_data
    args.doc.applyTemplate(data, False)
    return params


def match(j, args, params, tags, tasklet):
    return True
