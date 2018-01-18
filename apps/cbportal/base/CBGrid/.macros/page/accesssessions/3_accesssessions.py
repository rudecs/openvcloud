def main(j, args, params, tags, tasklet):
    remote = args.requestContext.params.get('ip')
    oauth = j.clients.oauth.get(instance='itsyouonline')
    jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    if jwt:
        table_data = j.apps.cloudbroker.zeroaccess.listSessions(remote=remote, ctx=args.requestContext)
    else:
        table_data = [['No jwt found please login and out', '', '', '', '']]

    page = args.page

    fieldnames = ['Session ID', 'Username', 'Remote', 'Start', 'End']
    if not table_data:
        table_data = [['No sessions for this node', '', '', '', '']]
    page.addList(table_data, fieldnames)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
