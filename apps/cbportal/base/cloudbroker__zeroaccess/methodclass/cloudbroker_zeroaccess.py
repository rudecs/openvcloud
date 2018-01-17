from JumpScale import j
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
from JumpScale.portal.portal import exceptions
from JumpScale.baselib.http_client.HttpClient import HTTPError
import requests
import datetime

class cloudbroker_zeroaccess(BaseActor):
    """
    Operator actions for interventions specific to a user
    """
    def __init__(self):
        super(cloudbroker_zeroaccess, self).__init__()
        self.zeroaccessurl = 'http://172.17.0.1:5000'

    def listSessions(self, query='', page=None, user='', remote='', **kwargs):
        """
        List available 0-access sessions
        """
        params = {
            'query': query,
            'page': page,
            'user': user,
            'remote': remote
        }

        def get_nodes_dict():
            """
            get dict returnig  necessary nodes information
            """
            ocl = j.clients.osis.getNamespace('system')
            nodes = {}
            for node_id in ocl.node.list():
                node = ocl.node.get(node_id)
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

        ctx = kwargs['ctx']
        jwt = ctx.env['beaker.session'].get('jwt')
        resp = requests.get('{}/sessions'.format(self.zeroaccessurl), params=params, headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        result = resp.json()
        if resp.status_code != 200:
            result_data = [['Can not get data from 0-access server jwt may be expired please logout and login again', '', '', '', '']]
        elif result['total_pages'] == 0:
                result_data = result['page']
        else:
            sessions = result['page']['sessions']
            result_data = list()
            nodes = get_nodes_dict()
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
                    result_data.append(itemdata)
        return result_data

    def provision(self, remote, **kwargs):
        ctx = kwargs['ctx']
        jwt = ctx.env['beaker.session'].get('jwt')
        result = {}
        resp = requests.get('{0}/provision/{1}'.format(self.zeroaccessurl, remote), headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            result = resp.json()
        return result

    def downloadSession(self, session_id, **kwargs):
        ctx = kwargs['ctx']
        result = ""
        jwt = ctx.env['beaker.session'].get('jwt')
        resp = requests.get('{0}sessions/{1}'.format(self.zeroaccessurl, session_id), headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            result = resp.content
        return result
        
    def getSessionInitTime(self, **kwargs):
        ctx = kwargs['ctx']
        result = ""
        jwt = ctx.env['beaker.session'].get('jwt')
        resp = requests.get('{}/server/config'.format(self.zeroaccessurl), headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            result = resp.json()
        return result

    def sessionTextSearch(self, query, **kwargs):
        ctx = kwargs['ctx']
        result = ""
        jwt = ctx.env['beaker.session'].get('jwt')
        resp = requests.get('{}/sessions'.format(self.zeroaccessurl), params={'query': query}, headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            result = resp.json()
        return result
