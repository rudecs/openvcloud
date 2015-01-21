import requests
import hashlib
import json
ADMIN_PASS = #PLEASE FILL IN ADMIN PASS
authentication_params = {'resourceUri':'null', 'id':'null', 'sessionId':'null',  'username':'admin', 'password':ADMIN_PASS}

def authenticate(request):
  headers = {'content-type': 'application/json'}
  response = request.post('http://173.240.9.179/api/sessions/',data=json.dumps(authentication_params), headers=headers)
  if response.status_code != 201:
    raise
  else:
    return (request, response.json())

def get_users(request):
  headers = {'content-type': 'application/json'}
  response = request.get('http://173.240.9.179/api/users/',headers=headers)
  if response.status_code != 200:
    raise
  else:
    return (request, response.json())

def add_app(request, command, description, icon, name, key, protocol):
  headers = {'content-type': 'application/json', 'X-CSRFTOKEN': request.cookies.get('csrftoken')}
  data = {
            'command': command,
            'description': description,
            'host':'test',
            'icon': icon,
            'name': name,
            'key': key,
            'protocol': protocol
        }

  response = request.post('http://173.240.9.179/api/apps/',data=json.dumps(data), headers=headers)
  return (request, response.json())

def add_app_to_server(request,appkey,appname,description,server_id):
  headers = {'content-type': 'application/json', 'X-CSRFTOKEN': request.cookies.get('csrftoken')}
  data = {
            'key': appkey,
            'description': description,
            'name':appname
        }
  response = request.post('http://173.240.9.179/appconnector/apps',data=json.dumps(data), headers=headers)
  if response.status_code != 201:
    raise
  else:
    data = {'apps': {}}
    data['apps'][response.json()['id']] = True
    url = 'http://173.240.9.179/appconnector/servers/%i/apps' % server_id
    response = request.put(url,data=json.dumps(data), headers=headers)
  return (request, response.json())




if __name__ == '__main__':
    request = requests.Session()
    request, authentication_data = authenticate(request)
    #request, users = get_users(request)
    #for i in range(3,4):
    #    request, app = add_app(request, '/usr/bin/xterm -hold -e ssh root@cpu0%s.york1.vscalers.com' % i, 'SSH to CPU0%s on YORK1' % i, '/app/icon/appcatalog_appicon/ssh-logo.jpg','SSHCPU0%sYORK1' % i, 'SSHCPU0%sYORK1' % i,'xRDP')
    #    request, admin_app = add_app_to_server(request, 'SSHCPU0%sYORK1' % i , 'SSHCPU0%sYORK1' % i, 'SSH session to CPU0%s York1' % i, 1)
    for i in range(10,21):
        request, app = add_app(request, '/usr/bin/virt-manager --no-fork -c qemu+ssh://root@cpu%s.york1.vscalers.com/system' % i, 'Libvirt to CPU%s on YORK1' % i, '/app/icon/appcatalog_appicon/virt-manager.png','LIBVIRTCPU%sYORK1' % i, 'LIBVIRTCPU%sYORK1' % i,'xRDP')
        request, admin_app = add_app_to_server(request, 'LIBVIRTCPU%sYORK1' % i , 'LIBVIRTCPU%sYORK1' % i, 'LIBVIRT session to CPU%s York1' % i, 1)










    import ipdb
    ipdb.set_trace()
    print response



    #createClient()
