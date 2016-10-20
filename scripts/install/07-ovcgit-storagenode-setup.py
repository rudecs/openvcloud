from JumpScale import j
from optparse import OptionParser
import json
import urllib
import sys
import time

""" FIXME: Move me """


def info(text):
    print '\033[1;36m[*] %s\033[0m' % text


def notice(text):
    print '\033[1;34m[+] %s\033[0m' % text


def warning(text):
    print '\033[1;33m[-] %s\033[0m' % text


def success(text):
    print '\033[1;32m[+] %s\033[0m' % text


def enableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = False
    j.remote.cuisine.api.fabric.state.output['running'] = False


def disableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = True
    j.remote.cuisine.api.fabric.state.output['running'] = True

parser = OptionParser()
parser.add_option("-n", "--node", dest="node", help="node id")
parser.add_option("-t", "--type", dest="type", default="storagenode", help="Node type storagenode or storagerouter")
(options, args) = parser.parse_args()

options.type = options.type.split(',')

print '[+] loading nodes list'

openvcloud = j.clients.openvcloud.get()
nodes = openvcloud.getRemoteNodes()

print '[+] found: %d nodes' % len(nodes)

if options.node is None:
    print '[-] no node available found'
    sys.exit(1)

print '[+] searching for node: %s' % options.node

for service in nodes:
    if service.instance == options.node:
        break
else:
    print '[-] node not found'
    sys.exit(1)

nodename = options.node

master = ''

print '[+] loading configuration for node: %s' % nodename

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

password = settings.getStr('instance.ovc.password')

print '[+] node name: %s' % nodename

"""
storagenode all-in-one data configuration
"""
info('building storagenode configuration')

data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.grid.id': configure.getInt('instance.grid.id'),
}

print '[+] building reverse ssh tunnel settings'

refsrv = j.atyourservice.findServices(name='node.ssh', instance='ovc_reflector')

print '[+] building reverse ssh tunnel settings'

refsrv = j.atyourservice.findServices(name='node.ssh', instance='ovc_reflector')

if len(refsrv) > 0:
    autossh = True
    reflector = refsrv[0]

    refaddress = reflector.hrd.getStr('instance.ip')
    refport = reflector.hrd.getStr('instance.ssh.publicport')

    if refport == None:
        print '[-] cannot find reflector public ssh port'
        sys.exit(1)

    # find autossh of this node
    autossh = next(iter(j.atyourservice.findServices(name='autossh', instance=nodename)), None)
    if not autossh:
        print '[-] cannot find auto ssh of node'
        sys.exit(1)

    remoteport = autossh.hrd.getInt('instance.remote.port') - 21000 + 2000
    data_autossh = {
            'instance.local.address': 'localhost',
            'instance.local.port': '2001',
            'instance.remote.address': settings.getStr('instance.ovc.cloudip'),
            'instance.remote.bind': refaddress,
            'instance.remote.connection.port': refport,
            'instance.remote.login': 'guest',
            'instance.remote.port': remoteport,
    }

    print '[+] autossh tunnel port: %s' % data_autossh['instance.remote.port']
    print '[+] cpunode reflector address: %s, %s' % (refaddress, refport)

else:
    autossh = False
    print '[-] reflector not found, skipping autossh'


print '[+]'
print '[+] storagenode cloudspace       : %s' % data_cpu['instance.param.master.addr']
print '[+] storagenode grid id          : %s' % data_cpu['instance.param.grid.id']
print '[+]'

print '[+] building remote host connection'

nodeService = j.atyourservice.get(name='node.ssh', instance=nodename)

raw_input("Press key to continue.")

#
# checking if openvstorage is correctly installed
#

notice('installing storage node: %s' % options.type)
for storagetype in options.type:
    packagename = 'cb_storagenode_aio' if storagetype == 'storagenode' else 'cb_storagedriver_aio'
    temp = j.atyourservice.new(name=packagename, args=data_cpu, parent=nodeService)
    temp.consume('node', nodeService.instance)
    temp.install(deps=True)

if 'storagedriver' in options.type:
    client = nodeService.actions.getSSHClient(nodeService)
    if client.file_exists('/etc/init/ovs-webapp-api.conf'):
        if autossh:
            temp = j.atyourservice.new(name='autossh', instance='http_proxy_ovs', args=data_autossh, parent=nodeService)
            temp.consume('node', nodeService.instance)
            temp.install(deps=True)

        nodeService.execute("python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-create-user.py")

        # loading ovc_master oauth server keys
        oauthfile = '/tmp/oauthserver.hrd'

        oauthService = j.atyourservice.get(name='node.ssh', instance='ovc_master')
        oauthService.actions.download(oauthService, '/opt/jumpscale7/hrd/apps/openvcloud__oauthserver__main/service.hrd', oauthfile)

        info('building oauth configuration')

        oauth = j.core.hrd.get(oauthfile, prefixWithName=True)
        oauth_url = oauth.get('instance.oauth.url')
        oauth_url = oauth_url.strip('/')

        oauth_authorize_uri = '%s/login/oauth/authorize' % oauth_url
        oauth_token_uri = '%s/login/oauth/access_token' % oauth_url

        oauth_ovs_id = oauth.get('instance.oauth.clients.ovs.id')
        oauth_ovs_secret = oauth.get('instance.oauth.clients.ovs.secret')

        print '[+] oauth url      : %s' % oauth_url
        print '[+] oauth authorize: %s' % oauth_authorize_uri
        print '[+] oauth token    : %s' % oauth_token_uri
        print '[+] oauth id       : %s' % oauth_ovs_id
        print '[+] oauth secret   : %s' % oauth_ovs_secret

        data_oauth = {'instance.oauth.id': oauth_ovs_id,
                      'instance.oauth.secret': oauth_ovs_secret,
                      'instance.oauth.authorize_uri': oauth_authorize_uri,
                      'instance.oauth.token_uri': oauth_token_uri}
                                                                                                            
        temp = j.atyourservice.new(name='openvstorage_oauth', instance='main', args=data_oauth, parent=nodeService)
        temp.consume('node', nodeService.instance)
        temp.install(deps=True)


notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')
