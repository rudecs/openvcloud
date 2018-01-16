import requests
from jose import jwt as jose_jwt
import datetime
import ast

def main(j, args, params, tags, tasklet):
    page = args.page
    import base64
    page.addCSS('/jslib/asciinema/asciinema-player.css', media='screen')
    page.addJS('/jslib/asciinema/asciinema-player.js')
    jwt = args.requestContext.env['beaker.session'].get('jwt')
    session_id = args.requestContext.params.get('sessionid')
    if jwt:
        jwt_data = jose_jwt.get_unverified_claims(jwt)
        jwt_data = ast.literal_eval(jwt_data)
        exp_date = datetime.datetime.fromtimestamp(jwt_data["exp"])
        now = datetime.datetime.now()
        if now > exp_date:
            url = 'https://itsyou.online/v1/oauth/jwt/refresh'
            headers = {'Authorization': 'bearer {0}'.format(jwt)}
            resp = requests.get(url, headers=headers)
            jwt = ""
            if resp.status_code == 200:
                jwt = resp.content
        resp = requests.get('http://0access:5001/sessions/{}'.format(session_id), headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            html = '<asciinema-player src="data:application/json;base64,{}"></asciinema-player>'.format(base64.b64encode(resp.content))
            page.addHTML(html)
        else:
            html = 'Can not get session {}'.format(session_id)
            page.addCodeBlock('Failed to retrieve session from server, may be JWT expired, please logout and login to renew')
    else:
        page.addCodeBlock('No JWT found please, login and logout to renew')
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
