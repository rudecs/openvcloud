import requests

def main(j, args, params, tags, tasklet):
    page = args.page
    import base64
    import json
    page.addCSS('/jslib/asciinema/asciinema-player.css', media='screen')
    page.addJS('/jslib/asciinema/asciinema-player.js')
    oauth = j.clients.oauth.get(instance='itsyouonline')
    jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    session_id = args.requestContext.params.get('sessionid')
    if jwt:
        session = j.apps.cloudbroker.zeroaccess.downloadSession(session_id=session_id, ctx=args.requestContext)
        if session:
            html = '<asciinema-player src="data:application/json;base64,{}"></asciinema-player>'.format(base64.b64encode(json.dumps(session)))
            page.addHTML(html)
        else:
            page.addCodeBlock("Recording for session {} can't be found".format(session_id))
    else:
        page.addCodeBlock('No JWT found please, login and logout to renew')
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
