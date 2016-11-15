from JumpScale import j
from optparse import OptionParser
import json
import sys
import time


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

j.console.info('loading nodes list')

openvcloud = j.clients.openvcloud.get()
nodes = openvcloud.getRemoteNodes()
j.console.success('found: %d nodes' % len(nodes))
sshNodeService = None

if options.node is None:
    j.console.info('performing autodetection of nodes')

    for service in nodes:
        childs = service.listChildren()
        if not childs.get('openvcloud'):
            j.console.success('found node not installed: %s' % service.instance)
            sshNodeService = service
            break

        if 'openvstorage' not in childs['openvcloud']:
            j.console.success('found node without openvstorage: %s' % service.instance)
            sshNodeService = service
            break
    else:
        j.console.warning('[-] no node available found')
        sys.exit(1)

    j.console.sucess('autodetected: \033[1;33m%s\033[0m' % sshNodeService.instance)
    j.console.notice(' if this is not what you want, you have 10 seconds to press CTRL+C to interrupt')
    time.sleep(10)
else:
    j.console.info('searching for node: %s' % options.node)
    try:
        sshNodeService = j.clients.openvcloud.getRemoteNode(options.node)
    except KeyError as e:
        j.console.warning('[-] node not found')
        sys.exit(1)

master = ''
if options.master is None and options.slave is None:
    j.console.info('autodetecting setup type')

    ovsMaster = j.atyourservice.findServices(domain='openvcloud', name='ovs_setup')

    if len(ovsMaster) > 0:
        j.console.info('master found, this will be a auto-setup slave configuration')
        masterService = j.application.getAppInstanceHRD(name='ovs_setup', instance='main', domain='openvcloud')
        options.slave = masterService.getStr('instance.ovs.master')
        masterNode = masterService.getStr('instance.ovs.masternode')

    else:
        j.console.info('master not found, this will be a auto-setup master configuration')
        options.master = True
        masterNode = None

if options.slave is not None:
    master = options.slave
    masterNode = None  # FIXME ?
    j.console.success('slave installation, master host: %s' % master)

if options.master is True:
    masterNode = None
    j.console.success('master installation')

j.console.info('setup will start... warm-up.')
time.sleep(3)

j.console.info('[+] loading configuration for node: %s' % node)

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

ovcproxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
ssl = j.application.getAppInstanceHRD(name='ssloffloader', instance='main', domain='openvcloud', parent=ovcproxy)

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
password = settings.getStr('instance.ovc.password')

j.console.info('node name: %s' % sshNodeService.instance)

if masterNode is None:
    masterNode = sshNodeService.instance

# loading ovc_master oauth server keys
oauthfile = '/tmp/oauthserver.hrd'

oauthService = j.atyourservice.get(name='node.ssh', instance='ovc_master')
oauthService.actions.download(oauthService, '/opt/jumpscale7/hrd/apps/openvcloud__oauthserver__main/service.hrd', oauthfile)

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

"""
openvstorage data configuration
"""
j.console.info('building openvstorage configuration')

enableQuiet()

backplane1 = sshNodeService.execute("ip -4 -o addr show dev backplane1 | awk '{ print $4 }' | cut -d'/' -f 1")
lastipbyte = backplane1.split('.')[-1]
j.console.info('node backplane1 address: %s' % backplane1)

data_ovs = {
    'instance.targetip': backplane1,
    # 'instance.targetpasswd': password,
    'instance.targetpasswd': 'rooter',  # use use hardcoded rooter root password for nodes
    'instance.clustername': environment,
    'instance.masterip': master,
    'instance.nodeid': '%03d' % node,
    # 'instance.masterpasswd': password,
    'instance.masterpasswd': 'rooter',  # use use hardcoded rooter root password for nodes
    'instance.oauth.id': oauth_ovs_id,
    'instance.oauth.secret': oauth_ovs_secret,
    'instance.oauth.authorize_uri': oauth_authorize_uri,
    'instance.oauth.token_uri': oauth_token_uri,
}


"""
scaleout network data configuration
"""
j.console.info('building network configuration')

public_vlan = '2312' if options.vlan is None else options.vlan
mgmt_vlan = '2314'
vxbackend_vlan = '2313'

j.console.info('public vlan: %s' % public_vlan)
j.console.info('management vlan: %s' % mgmt_vlan)
j.console.info('vxbackend vlan: %s' % vxbackend_vlan)

data_net = {
    'instance.netconfig.public_backplane.interfacename': 'backplane1',
    'instance.netconfig.gw_mgmt_backplane.interfacename': 'backplane1',
    'instance.netconfig.vxbackend.interfacename': 'backplane1',
    'instance.netconfig.public.vlanid': public_vlan,
    'instance.netconfig.gw_mgmt.vlanid': mgmt_vlan,
    'instance.netconfig.vxbackend.vlanid': vxbackend_vlan,
    'instance.netconfig.gw_mgmt.ipaddr': '10.199.0.%d/22' % lastipbyte,
    'instance.netconfig.vxbackend.ipaddr': '10.240.0.%d/16' % lastipbyte,
}

"""
cpunode all-in-one data configuration
"""
j.console.info('building cpunode configuration')

vncurl = 'https://novnc-%s.%s' % (sshNodeService.parent.instance, settings.getStr('instance.ovc.domain'))
data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.network.gw_mgmt_ip': '10.199.0.2/22',
    'instance.param.grid.id': options.gid or configure.getInt('instance.grid.id'),
    'instance.vnc.url': vncurl,
}

j.console.info('building reverse ssh tunnel settings')
j.clients.openvcloud.configureNginxProxy(sshNodeService, settings)

j.console.info('')
j.console.info(' openvstorage cluster     : %s' % data_ovs['instance.clustername'])
j.console.info(' cpunode cloudspace       : %s' % data_cpu['instance.param.master.addr'])
j.console.info(' cpunode novnc address    : %s' % data_cpu['instance.vnc.url'])
j.console.info(' cpunode grid id          : %s' % data_cpu['instance.param.grid.id'])
j.console.info('')
j.console.info(' building remote host connection')

if not options.noovs:
    if options.slave:
        j.console.info('testing connectivity to master node')
        ping = sshNodeService.execute('ping -s 10000 -c 1 -w 1 %s 2>&1 > /dev/null || echo "failed"' % options.slave)

        if ping == 'failed':
            j.console.warning('cannot ping (10k) remote host: %s, please check mtu and link state' % options.slave)
            j.application.stop(1)

    disableQuiet()

    """
    WARNING: After this point, changes will be applied.
             Before this point, you can run the script without affecting any part of the system.
    """

    j.console.notice('installing openvstorage')
    temp = j.atyourservice.new(name='openvstorage', args=data_ovs, parent=sshNodeService)
    temp.consume('node', sshNodeService.instance)
    temp.install(deps=True)

    #
    # checking if openvstorage is correctly installed
    #
    enableQuiet()
    content = sshNodeService.execute('cat /opt/OpenvStorage/config/ovs.json')
    result = json.loads(content)
    disableQuiet()

    if not result['core']['setupcompleted']:
        j.console.warning('openvstorage not installed correctly, nice try')
        j.application.stop()

    j.console.success('openvstorage installed, well done')

j.console.notice('installing network')
temp = j.atyourservice.new(name='scaleout_networkconfig', args=data_net, parent=sshNodeService)
temp.consume('node', sshNodeService.instance)
temp.install(deps=True)

j.console.notice('installing cpu node')
temp = j.atyourservice.new(name='cb_cpunode_aio', args=data_cpu, parent=sshNodeService)
temp.consume('node', sshNodeService.instance)
temp.install(deps=True)

# Saving stuff
if not options.noovs:
    if options.master is True:
        j.console.info('saving master settings')

        ovsdata = {
            'ovs.master': backplane1,
            'ovs.masternode': sshNodeService.instance,
            'ovs.environment': environment
        }

        setupService = j.atyourservice.new(name='ovs_setup', instance='main', args=ovsdata)
        setupService.install(reinstall=False)

        sshNodeService.execute("python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-create-user.py")
        # disable bootstrap exposed port, we should not add node anymore
        # this is a security fix
        clients = j.atyourservice.findServices(name='ms1_client', instance='main')
        if len(clients):
            j.console.info('checking ovcgit security')

            ms1config = j.application.getAppInstanceHRD(name='ms1_client', instance='main')

            ms1 = {
                'secret': ms1config.getStr('instance.param.secret'),
                'location': ms1config.getStr('instance.param.location'),
                'cloudspace': ms1config.getStr('instance.param.cloudspace')
            }

            vm = j.clients.vm.get('ms1', ms1)
            ms1api = vm._mother['api']  # FIXME: this is a bad way
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

    j.console.notice('saving ovs setup stuff to the node')
    temp = j.atyourservice.new(name='ovs_setup', instance='main', args=ovsdata)
    temp.consume('node', sshNodeService.instance)
    temp.install(deps=True)

    j.console.notice('installing alba healtcheck credential')
    content = sshNodeService.execute('python /opt/code/github/0-complexity/openvcloud/scripts/ovs/alba-get-user.py')
    user = json.loads(content)

    albadata = {
        'instance.client_id': user['client'],
        'instance.client_secret': user['secret']
    }

    temp = j.atyourservice.new(name='ovs_alba_oauthclient', args=albadata, parent=sshNodeService)
    temp.consume('node', sshNodeService.instance)
    temp.install(deps=True)

j.console.notice('restarting some services')
sshNodeService.execute('ays restart -n nginx')

j.console.notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

j.console.notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')

j.console.success('node installed, backplane ip address was: %s' % backplane1)
