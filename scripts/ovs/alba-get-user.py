from JumpScale import j
import json

from ovs.dal.hybrids.user import User
from ovs.dal.hybrids.client import Client
from ovs.dal.lists.userlist import UserList

def user():
    admin = UserList.get_user_by_username('admin')

    alba_client = None
    alba_secret = None

    clients = admin.clients

    for client in clients:
        if client.name == 'alba':
            alba_client = client.client_id
            alba_secret = client.client_secret

    if alba_client is None:
        return {'error': 'user not found'}

    return {'client': alba_client, 'secret': alba_secret}
    
credentials = user()
print json.dumps(credentials)
