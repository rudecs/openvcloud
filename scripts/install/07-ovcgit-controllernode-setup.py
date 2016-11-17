from JumpScale import j
from optparse import OptionParser
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
parser.add_option("-g", "--grid-id", dest="gid", type=int, help="Grid ID to join")
(options, args) = parser.parse_args()

openvcloud = j.clients.openvcloud.get()

try:
    node = openvcloud.getRemoteNode(options.node)
except KeyError as e:
    j.console.warning(e)
    sys.exit(1)

nodename = options.node

j.console.info('setup will start... warm-up.')
time.sleep(3)

j.console.info('loading configuration for node: %s' % node)

# loading settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
configure = j.application.getAppInstanceHRD(name='ovc_configure_aio', instance='main', domain='openvcloud')

ovcproxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
ovcmaster = j.atyourservice.get(name='node.ssh', instance='ovc_master')
ssl = j.application.getAppInstanceHRD(name='ssloffloader', instance='main', domain='openvcloud', parent=ovcproxy)

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
password = settings.getStr('instance.ovc.password')

j.console.info('building reverse ssh tunnel settings')
refsrv = j.atyourservice.findServices(name='node.ssh', instance='ovc_reflector')

if len(refsrv) > 0:
    autossh = True
    reflector = refsrv[0]

    refaddress = reflector.hrd.getStr('instance.ip')
    refport = reflector.hrd.getStr('instance.ssh.publicport')

    if refport is None:
        j.console.warning('cannot find reflector public ssh port')
        sys.exit(1)

    # find autossh of this node
    autossh = next(iter(j.atyourservice.findServices(name='autossh', instance=nodename)), None)
    if not autossh:
        print('[-] cannot find auto ssh of node')
        sys.exit(1)

    remoteport = autossh.hrd.getInt('instance.remote.port') - 21000 + 2000
    data_autossh = {'instance.local.address': 'localhost',
                    'instance.local.port': '8086',
                    'instance.remote.address': settings.getStr('instance.ovc.cloudip'),
                    'instance.remote.bind': refaddress,
                    'instance.remote.connection.port': refport,
                    'instance.remote.login': 'guest',
                    'instance.remote.port': remoteport,
                    }

    print('[+] autossh tunnel port: %s' % data_autossh['instance.remote.port'])
    print('[+] cpunode reflector address: %s, %s' % (refaddress, refport))
    temp = j.atyourservice.new(name='autossh', instance='http_grafana', args=data_autossh, parent=node)
    temp.consume('node', node.instance)
    temp.install(deps=True)
    dashboard_data = {'instance.datasource.ip': refaddress,
                      'instance.datasource.port': remoteport,
                      }

else:
    autossh = False
    print('[-] reflector not found')
    mgmtip = node.execute("ip -4 -o addr show dev mgmt | awk '{ print $4 }' | cut -d'/' -f 1")
    dashboard_data = {'instance.datasource.ip': mgmtip,
                      'instance.datasource.port': 8086,
                      }

data_controller = {
    'instance.param.rootpasswd': password,
    'instance.param.master.addr': settings.getStr('instance.ovc.cloudip'),
    'instance.param.grid.id': options.gid or configure.getInt('instance.grid.id'),
}

j.console.notice('installing controller node')
temp = j.atyourservice.new(name='cb_controller', args=data_controller, parent=node)
temp.consume('node', node.instance)
temp.install(deps=True)

j.console.notice('installing dashboards for controller')
location = node.parent.instance
temp = j.atyourservice.new(name='controller_dashboards', args=dashboard_data, parent=ovcmaster, instance=location)
temp.consume('node', ovcmaster.instance)
temp.install(deps=True)


j.console.notice('commit changes')
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')

j.console.success('controller node installed.')
