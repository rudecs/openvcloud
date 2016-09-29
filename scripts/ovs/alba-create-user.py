from JumpScale import j
import random
import string
import sys
import time

from ovs.dal.hybrids.user import User
from ovs.dal.hybrids.client import Client
from ovs.dal.hybrids.j_roleclient import RoleClient
from ovs.dal.lists.userlist import UserList
from ovs.dal.lists.storagerouterlist import StorageRouterList

"""
Add credentials for alba oauth2
"""
def user():
    admin = UserList.get_user_by_username('admin')
    print '[+] admin guid: %s' % admin.guid

    alba_client = None
    alba_secret = None

    clients = admin.clients

    for client in clients:
        if client.name == 'alba':
            alba_client = client.client_id
            alba_secret = client.client_secret
            print '[+] alba client already set'

    if alba_client is None:
        print '[+] adding "alba" oauth2 client'
        choice = string.ascii_letters + string.digits

        # Creating user
        alclient = Client()
        alclient.ovs_type = 'USER'
        alclient.name = 'alba'
        alclient.grant_type = 'CLIENT_CREDENTIALS'
        alclient.client_secret = ''.join(random.choice(choice) for _ in range(64))
        alclient.user = admin
        alclient.save()

        # Adding roles
        for junction in admin.group.roles:
            roleclient = RoleClient()
            roleclient.client = alclient
            roleclient.role = junction.role
            roleclient.save()

        alba_client = alclient.client_id
        alba_secret = alclient.client_secret

    return {'client_id': alba_client, 'client_secret': alba_secret}


def get_management_ip():
    localips = j.system.net.getIpAddresses()
    for storagerouter in StorageRouterList.get_storagerouters():
        if storagerouter.ip in localips:
            return storagerouter.ip


if __name__ == '__main__':
    print '[+] managing users'

    scl = j.clients.osis.getNamespace('system')
    grid = scl.grid.get(j.application.whoAmI.gid)
    credentials = grid.settings.get('ovs_credentials')
    ips = set()
    if credentials is None:
        credentials = user()
    else:
        ips = set(credentials.get('ips', []))

    ips.add(get_management_ip())
    credentials['ips'] = list(ips)
    grid.settings['ovs_credentials'] = credentials
    scl.grid.set(grid)

    print '[+] alba client id: %s' % credentials['client_id']
    print '[+] alba secret: %s' % credentials['client_secret']
