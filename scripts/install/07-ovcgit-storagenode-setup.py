from JumpScale import j
from argparse import ArgumentParser
import sys


def enableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = False
    j.remote.cuisine.api.fabric.state.output['running'] = False


def disableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = True
    j.remote.cuisine.api.fabric.state.output['running'] = True

parser = ArgumentParser()
parser.add_argument("-n", "--node", dest="node", help="node id", required=True)
parser.add_argument("-t", "--type", dest="type", default="storagenode", help="Node type storagenode or storagerouter")
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

data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.grid.id': configure.getInt('instance.grid.id'),
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

        oauthService = j.atyourservice.get(name='node.ssh', instance='ovc_master')
        oauthService.actions.download(oauthService, '/opt/jumpscale7/hrd/apps/openvcloud__oauthserver__main/service.hrd',
                                      oauthfile)

        j.console.info('building oauth configuration')

        oauth = j.core.hrd.get(oauthfile, prefixWithName=True)
        oauth_url = oauth.get('instance.oauth.url')
        oauth_url = oauth_url.strip('/')

        oauth_authorize_uri = '%s/login/oauth/authorize' % oauth_url
        oauth_token_uri = '%s/login/oauth/access_token' % oauth_url

        oauth_ovs_id = oauth.get('instance.oauth.clients.ovs.id')
        oauth_ovs_secret = oauth.get('instance.oauth.clients.ovs.secret')

        j.console.info('oauth url      : %s' % oauth_url)
        j.console.info('oauth authorize: %s' % oauth_authorize_uri)
        j.console.info('oauth token    : %s' % oauth_token_uri)
        j.console.info('oauth id       : %s' % oauth_ovs_id)
        j.console.info('oauth secret   : %s' % oauth_ovs_secret)

        data_oauth = {'instance.oauth.id': oauth_ovs_id,
                      'instance.oauth.secret': oauth_ovs_secret,
                      'instance.oauth.authorize_uri': oauth_authorize_uri,
                      'instance.oauth.token_uri': oauth_token_uri}

        temp = j.atyourservice.new(name='openvstorage_oauth', instance='main', args=data_oauth, parent=node)
        temp.consume('node', node.instance)
        temp.install(deps=True)


j.console.notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

j.console.notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')
