from JumpScale import j
import re
import json
import ssl
import sys
import urllib2
import urllib
import json
import base64

organization = "openvstorage"
descr = 'Perform Disk checks on ALBA'
author = "hamdy.farag@codescalers.com"
order = 1
enable = True
async = True
log = True
queue = 'io'
period = 30 * 60
roles = ['storagenode']
category = "monitor.healthcheck"

def action():
    ip = '127.0.0.1'
    ovs_alba = j.atyourservice.get(name='ovs_alba_oauthclient', instance='main')
    client_id = ovs_alba.hrd.getStr('instance.client_id')
    client_secret = ovs_alba.hrd.getStr('instance.client_secret')
    sys.path.append('/opt/OpenvStorage')
    headers = {'Accept': 'application/json'}
    auth_url = 'https://{0}/api/oauth2/token/'.format(ip)
    base_url = 'https://{0}/api/'.format(ip)
    
    headers['Authorization'] = 'basic {0}'.format(base64.b64encode('{0}:{1}'.format(client_id, client_secret)))
    request = urllib2.Request(auth_url, data=urllib.urlencode({'grant_type': 'client_credentials'}), headers=headers)
    response = urllib2.urlopen(request).read()
    
    token = json.loads(response)['access_token']
    
    headers['Authorization'] = 'Bearer {0}'.format(token)
    headers['Accept'] = 'application/json; version=*'
    
    request = urllib2.Request(base_url + '/alba/backends', None, headers=headers)
    response = urllib2.urlopen(request).read()
    backends = json.loads(response)['data']
    result = []
    for backend in backends:
        request = urllib2.Request(base_url + '/alba/backends/%s' % backend, None, headers=headers)
        response = urllib2.urlopen(request).read()
        data = json.loads(response)

        for disk in data['all_disks']:
            if disk['state']['state'] == 'ok':
                continue
            r = {}
            r['category'] = 'ALBA healthcheck'
            r['state'] = disk['state']['state']
            r['message'] = 'OVS ALBA Backend %s  DISK %s : %s' % (data['name'], disk['name'], disk['state']['detail'])
            result.append(r)
            eco = j.errorconditionhandler.getErrorConditionObject(msg=r['message'], category='monitoring', level=1, type='OPERATIONS')
            eco.process()
    if not result:
        result.append({'category' : 'ALBA healthcheck', 'state':'OK', 'message':'ALL disjs are OK'})
    return result

if __name__ == '__main__':
    print action()