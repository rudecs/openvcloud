from JumpScale import j
from argparse import ArgumentParser
import sys
import time


def enableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = False
    j.remote.cuisine.api.fabric.state.output['running'] = False


def disableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = True
    j.remote.cuisine.api.fabric.state.output['running'] = True

parser = ArgumentParser()
parser.add_argument("-n", "--node", dest="node", help="node id", required=True)
parser.add_argument("-v", "--vlan", dest="vlan", help="public vlan id", default='2312')
parser.add_argument("-g", "--grid-id", dest="gid", type=int, help="Grid ID to join")
options = parser.parse_args()

openvcloud = j.clients.openvcloud.get()

try:
    node = openvcloud.getRemoteNode(options.node)
except KeyError as e:
    j.console.warning('node not found')
    sys.exit(1)

j.console.info('setup will start... warm-up.')
time.sleep(3)

j.console.info('loading configuration for node: %s' % node.instance)

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

ovcproxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
ssl = j.application.getAppInstanceHRD(name='ssloffloader', instance='main', domain='openvcloud', parent=ovcproxy)

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
password = settings.getStr('instance.ovc.password')

enableQuiet()

backplane1 = node.execute("ip -4 -o addr show dev backplane1 | awk '{ print $4 }' | cut -d'/' -f 1")
lastipbyte = backplane1.split('.')[-1]
j.console.info('node backplane1 address: %s' % backplane1)

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
    'instance.netconfig.gw_mgmt.ipaddr': '10.199.0.%s/22' % lastipbyte,
    'instance.netconfig.vxbackend.ipaddr': '10.240.0.%s/16' % lastipbyte,
}

"""
cpunode all-in-one data configuration
"""
j.console.info('building cpunode configuration')

vncurl = 'https://novnc-%s.%s' % (node.parent.instance, settings.getStr('instance.ovc.domain'))
data_cpu = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.network.gw_mgmt_ip': '10.199.0.%s/22' % lastipbyte,
    'instance.param.grid.id': options.gid or configure.getInt('instance.grid.id'),
    'instance.vnc.url': vncurl,
}

j.console.notice('installing network')
temp = j.atyourservice.new(name='scaleout_networkconfig', args=data_net, parent=node)
temp.consume('node', node.instance)
temp.install(deps=True)

j.console.notice('installing cpu node')
temp = j.atyourservice.new(name='cb_cpunode_aio', args=data_cpu, parent=node)
temp.consume('node', node.instance)
temp.install(deps=True)

j.console.notice('restarting some services')
node.execute('ays restart -n nginx')

j.console.notice('updating proxy')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/proxy/update-config.py', True, True)

j.console.notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')

j.console.success('node installed, backplane ip address was: %s' % backplane1)
