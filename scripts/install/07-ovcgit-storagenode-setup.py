from JumpScale import j
import os
from argparse import ArgumentParser
import sys


parser = ArgumentParser()
parser.add_argument("-n", "--node", dest="node", help="node id", required=True)
parser.add_argument("-t", "--type", dest="type", default="storagenode", help="Node type storagenode or storagerouter")
parser.add_argument("-g", "--grid-id", dest="gid", type=int, help="Grid ID to join")
options = parser.parse_args()

options.type = options.type.split(',')

openvcloud = j.clients.openvcloud.get()
try:
    node = openvcloud.getRemoteNode(options.node)
except KeyError as e:
    j.console.warning(e)
    sys.exit(1)

j.console.info('loading configuration for node: %s' % options.node)

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

password = settings.getStr('instance.ovc.password')

"""
storagenode all-in-one data configuration
"""
j.console.info('building storagenode configuration')

gid = options.gid or configure.getInt('instance.grid.id')
data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.grid.id': gid,
}


j.console.info('storagenode cloudspace       : %s' % data_cpu['instance.param.master.addr'])
j.console.info('storagenode grid id          : %s' % data_cpu['instance.param.grid.id'])
j.console.info('building remote host connection')

#
# checking if openvstorage is correctly installed
#

j.console.notice('installing storage node: %s' % options.type)
for storagetype in options.type:
    packagename = 'cb_storagenode_aio' if storagetype == 'storagenode' else 'cb_storagedriver_aio'
    temp = j.atyourservice.new(name=packagename, args=data_cpu, parent=node)
    temp.consume('node', node.instance)
    temp.install(deps=True)

if 'storagedriver' in options.type:
    client = node.actions.getSSHClient(node)
    if 'MASTER' in node.execute('ovs config get "ovs/framework/hosts/$(cat /etc/openvstorage_id)/type"'):
        openvcloud.configureNginxProxy(node, settings)
        node.execute("python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-create-user.py")

        # loading ovc_master oauth server keys
        oauthfile = '/tmp/oauthserver.hrd'
        ovc_iyo = j.atyourservice.get(name='ovc_itsyouonline')
        ovc_iyo.actions.prepare(ovc_iyo)
        environment = settings.get('ovc.environment')
        location = node.parent.instance
        apikeyname = 'ovs-{}-{}'.format(environment, location)
        domain = configure.hrd.get('instance.param.domain')
        ovscallbackurl = 'https://ovs-{}.{}/api/oauth2/redirect/'.format(location, domain)
        apikey = {'callbackURL': ovscallbackurl,
                  'clientCredentialsGrantType': False,
                  'label': apikeyname
                  }
        apikey = ovc_iyo.actions.configure_api_key(apikey)

        j.console.info('building oauth configuration')
        oauth_token_uri = os.path.join(ovc_iyo.baseurl, 'v1/oauth/access_token')
        oauth_authorize_uri = os.path.join(ovc_iyo.baseurl, 'v1/oauth/authorize')

        data_oauth = {'instance.oauth.id': ovc_iyo.client_id,
                      'instance.oauth.secret': apikey['secret'],
                      'instance.oauth.authorize_uri': oauth_authorize_uri,
                      'instance.oauth.token_uri': oauth_token_uri}

        temp = j.atyourservice.new(name='openvstorage_oauth', instance='main', args=data_oauth, parent=node)
        temp.consume('node', node.instance)
        temp.install(deps=True)


j.console.notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

j.console.notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')
