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
parser.add_option("-s", "--slave", dest="slave", help="slave setup, master ip address")
parser.add_option("-m", "--master", action="store_true", dest="master", help="master setup")
parser.add_option("-o", "--no-ovs", action="store_true", dest="noovs", default=False, help="don't install OpenvStorage")
parser.add_option("-v", "--vlan", dest="vlan", help="public vlan id")
parser.add_option("-g", "--grid-id", dest="gid", type=int, help="Grid ID to join")
(options, args) = parser.parse_args()

print '[+] loading nodes list'

openvcloud = j.clients.openvcloud.get()
nodes = openvcloud.getRemoteNodes()
node = None

print '[+] found: %d nodes' % len(nodes)

if options.node == None:
    info('performing autodetection of nodes')

    i = 1

    for service in nodes:
        childs = service.listChildren()
        if not childs.get('openvcloud'):
            print '[+] found node not installed: %s' % service.instance
            nodename = service.instance
            node = i
            break

        if 'openvstorage' not in childs['openvcloud']:
            print '[+] found node without openvstorage: %s' % service.instance
            nodename = service.instance
            node = i
            break

        i += 1

    if not node:
        print '[-] no node available found'
        sys.exit(1)

    print '[+] autodetected: \033[1;33m%s\033[0m (ID: %d)' % (nodename, node)
    print '[ ] if this is not what you want, you have 10 seconds to press CTRL+C to interrupt'

    time.sleep(10)

else:
    print '[+] searching for node: %s' % options.node

    i = 1

    for service in nodes:
        if service.instance == options.node:
            node = i
            print '[+] node found, id is: %d' % node
            break

        i += 1

    if not node:
        print '[-] node not found'
        sys.exit(1)

    nodename = options.node

master = ''

if options.master == None and options.slave == None:
    info('autodetecting setup type')

    ovsMaster = j.atyourservice.findServices(domain='openvcloud', name='ovs_setup')

    if len(ovsMaster) > 0:
        info('master found, this will be a auto-setup slave configuration')
        masterService = j.application.getAppInstanceHRD(name='ovs_setup', instance='main', domain='openvcloud')
        options.slave = masterService.getStr('instance.ovs.master')
        masterNode    = masterService.getStr('instance.ovs.masternode')

    else:
        info('master not found, this will be a auto-setup master configuration')
        options.master = True
        masterNode = None

if options.slave != None:
    master = options.slave
    masterNode = None # FIXME ?
    success('slave installation, master host: %s' % master)

if options.master == True:
    masterNode = None
    success('master installation')

print '[+] setup will start... warm-up.'
time.sleep(3)

print '[+] loading configuration for node: %s' % node

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

ovcproxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
ssl = j.application.getAppInstanceHRD(name='ssloffloader', instance='main', domain='openvcloud', parent=ovcproxy)

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
password = settings.getStr('instance.ovc.password')

print '[+] node name: %s' % nodename

if masterNode is None:
    masterNode = nodename

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

"""
openvstorage data configuration
"""
info('building openvstorage configuration')

enableQuiet()

sshNodeService = j.atyourservice.get(name='node.ssh', instance=nodename)
backplane1 = sshNodeService.execute("ip -4 -o addr show dev backplane1 | awk '{ print $4 }' | cut -d'/' -f 1")
print '[+] node backplane1 address: %s' % backplane1

data_ovs = {
    'instance.targetip': backplane1,
    # 'instance.targetpasswd': password,
    'instance.targetpasswd': 'rooter', # use use hardcoded rooter root password for nodes
    'instance.clustername': environment,
    'instance.masterip': master,
    'instance.nodeid': '%03d' % node,
    # 'instance.masterpasswd': password,
    'instance.masterpasswd': 'rooter', # use use hardcoded rooter root password for nodes
    'instance.oauth.id': oauth_ovs_id,
    'instance.oauth.secret': oauth_ovs_secret,
    'instance.oauth.authorize_uri': oauth_authorize_uri,
    'instance.oauth.token_uri': oauth_token_uri,
}


"""
scaleout network data configuration
"""
info('building network configuration')

public_vlan = '2312' if options.vlan == None else options.vlan
mgmt_vlan = '2314'
vxbackend_vlan = '2313'

print('[+] public vlan: %s' % public_vlan)
print('[+] management vlan: %s' % mgmt_vlan)
print('[+] vxbackend vlan: %s' % vxbackend_vlan)

data_net = {
    'instance.netconfig.public_backplane.interfacename': 'backplane1',
    'instance.netconfig.gw_mgmt_backplane.interfacename': 'backplane1',
    'instance.netconfig.vxbackend.interfacename': 'backplane1',
    'instance.netconfig.public.vlanid': public_vlan,
    'instance.netconfig.gw_mgmt.vlanid': mgmt_vlan,
    'instance.netconfig.vxbackend.vlanid': vxbackend_vlan,
    'instance.netconfig.gw_mgmt.ipaddr': '10.199.0.%d/22' % (int(node) + 10),
    'instance.netconfig.vxbackend.ipaddr': '10.240.0.%d/16' % (int(node) + 10),
}

"""
cpunode all-in-one data configuration
"""
info('building cpunode configuration')

vncurl = 'https://novnc-%s.%s' % (sshNodeService.parent.instance, settings.getStr('instance.ovc.domain'))
data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.network.gw_mgmt_ip': '10.199.0.2/22',
    'instance.param.grid.id': options.gid or configure.getInt('instance.grid.id'),
    'instance.vnc.url': vncurl,
}

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
print '[+] openvstorage cluster     : %s' % data_ovs['instance.clustername']
print '[+] cpunode cloudspace       : %s' % data_cpu['instance.param.master.addr']
print '[+] cpunode novnc address    : %s' % data_cpu['instance.vnc.url']
print '[+] cpunode grid id          : %s' % data_cpu['instance.param.grid.id']
print '[+]'

print '[+] building remote host connection'

nodeService = j.atyourservice.get(name='node.ssh', instance=nodename)

if not options.noovs:
    if options.slave:
        print '[+] testing connectivity to master node'
        ping = nodeService.execute('ping -s 10000 -c 1 -w 1 %s 2>&1 > /dev/null || echo "failed"' % options.slave)

        if ping == 'failed':
            warning('cannot ping (10k) remote host: %s, please check mtu and link state' % options.slave)
            j.application.stop()

    disableQuiet()

    """
    WARNING: After this point, changes will be applied.
             Before this point, you can run the script without affecting any part of the system.
    """

    notice('installing openvstorage')
    temp = j.atyourservice.new(name='openvstorage', args=data_ovs, parent=nodeService)
    temp.consume('node', nodeService.instance)
    temp.install(deps=True)

    #
    # checking if openvstorage is correctly installed
    #
    enableQuiet()
    content = nodeService.execute('cat /opt/OpenvStorage/config/ovs.json')
    result = json.loads(content)
    disableQuiet()

    if not result['core']['setupcompleted']:
        print '[-] openvstorage not installed correctly, nice try'
        j.application.stop()

    print '[+] openvstorage installed, well done'

notice('installing network')
temp = j.atyourservice.new(name='scaleout_networkconfig', args=data_net, parent=nodeService)
temp.consume('node', nodeService.instance)
temp.install(deps=True)

notice('installing cpu node')
temp = j.atyourservice.new(name='cb_cpunode_aio', args=data_cpu, parent=nodeService)
temp.consume('node', nodeService.instance)
temp.install(deps=True)

if autossh:
    temp = j.atyourservice.new(name='autossh', instance='http_proxy', args=data_autossh, parent=nodeService)
    temp.consume('node', nodeService.instance)
    temp.install(deps=True)

# Saving stuff
if not options.noovs:
    if options.master == True:
        print '[+] saving master settings'

        ovsdata = {
            'ovs.master': backplane1,
            'ovs.masternode': nodename,
            'ovs.environment': environment
        }

        setupService = j.atyourservice.new(name='ovs_setup', instance='main', args=ovsdata)
        setupService.install(reinstall=False)

        sshNodeService.execute("python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-create-user.py")

        # disable bootstrap exposed port, we should not add node anymore
        # this is a security fix
        clients = j.atyourservice.findServices(name='ms1_client', instance='main')
        if len(clients):
            print '[+] checking ovcgit security'

            ms1config = j.application.getAppInstanceHRD(name='ms1_client', instance='main')

            ms1 = {
                'secret': ms1config.getStr('instance.param.secret'),
                'location': ms1config.getStr('instance.param.location'),
                'cloudspace': ms1config.getStr('instance.param.cloudspace')
            }

            vm = j.clients.vm.get('ms1', ms1)
            ms1api = vm._mother['api'] # FIXME: this is a bad way
            ms1api.deleteTcpPortForwardRule(ms1['secret'], 'ovc_git', machinetcpport=5000, pubipport=5000)

        else:
            pass
            # TODO: remove port from xxx (not ms1)

    else:
        ovsdata = {
            'ovs.master': options.slave,
            'ovs.masternode': masterNode,
            'ovs.environment': environment
        }

    notice('saving ovs setup stuff to the node')
    temp = j.atyourservice.new(name='ovs_setup', instance='main', args=ovsdata)
    temp.consume('node', nodeService.instance)
    temp.install(deps=True)

    notice('installing alba healtcheck credential')
    content = nodeService.execute('python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-get-user.py')
    user = json.loads(content)

    albadata = {
        'instance.client_id': user['client'],
        'instance.client_secret': user['secret']
    }

    temp = j.atyourservice.new(name='ovs_alba_oauthclient', args=albadata, parent=nodeService)
    temp.consume('node', nodeService.instance)
    temp.install(deps=True)

notice('restarting some services')
sshNodeService.execute('ays restart -n nginx')

notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')

success('node installed, backplane ip address was: %s' % backplane1)
