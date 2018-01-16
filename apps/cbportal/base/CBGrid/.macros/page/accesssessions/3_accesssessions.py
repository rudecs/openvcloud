import requests
import json
import datetime
from jose import jwt as jose_jwt
import ast

def main(j, args, params, tags, tasklet):
    jwt = args.requestContext.env['beaker.session'].get('jwt')
    remote = args.requestContext.params.get('ip')
    def get_nodes_dict():
        ocl = j.clients.osis.getNamespace('system')
        nodes = {}
        for node_id in ocl.node.list():
            node = ocl.node.get(node_id)
            ip = ""
            if 'master' in node.roles:
                continue
            else:
                for addr in node.netaddr:
                    if addr['name'] == "backplane1":
                        nodes[addr['ip'][0]] = node.name
                        break
                else:
                    continue
        return nodes
    nodes = get_nodes_dict()
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
        resp = requests.get('http://0access:5001/sessions', params={'remote': remote}, headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            sessions = resp.json()['page']['sessions']
            aaData = list()
            for session in sessions:
                if session['start'] and session['end']:
                    session_id = session['href'].split('/')[-1]
                    itemdata = ['<a href="/cbgrid/Session Player?sessionid={sessionid}">{sessionid}</a>'.format(sessionid=session_id)]
                    itemdata.append(session['user']['username'])
                    if session['remote'] in nodes:
                        name = '<a href="/cbgrid/0-access Node?node={name}&ip={ip}">{name}</a>'.format(name=nodes[session['remote']], ip=session['remote'])
                        itemdata.append(name)
                    else:    
                        itemdata.append(session['remote'])
                    itemdata.append(datetime.datetime.fromtimestamp(session['start']).strftime('%Y-%m-%d %H:%M:%S'))
                    itemdata.append(datetime.datetime.fromtimestamp(session['end']).strftime('%Y-%m-%d %H:%M:%S'))    
                    aaData.append(itemdata)
        else:
            aaData = [['Can not get data from 0-access server jwt may be expired please logout and login again', '', '', '', '']]
    else:
        aaData = [['No jwt found please login and out', '', '', '', '']]

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Session ID', 'Username', 'Remote', 'Start', 'End']
    page.addList(aaData, fieldnames)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
