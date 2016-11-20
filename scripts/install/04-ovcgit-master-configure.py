from JumpScale import j
from argparse import ArgumentParser
import os
os.environ.pop('TMUX', None)  # allow install inside tmux

parser = ArgumentParser()
parser.add_argument("-g", "--gateway", dest="gateway", help="gateway ip address", required=True)
parser.add_argument("-s", "--start", dest="ipstart", help="public start ip address", required=True)
parser.add_argument("-e", "--end", dest="ipend", help="public env ip address", required=True)
parser.add_argument("-n", "--netmask", dest="netmask",
                    help="public env ip netmask (default 255.255.255.0)", default="255.255.255.0")
parser.add_argument("-G", "--gid", dest="gid", help="grid id", required=True, type=int)
parser.add_argument("-S", "--ssl", dest="ssl", help="set ssl keys method: wildcard or split")
options = parser.parse_args()

# options
if options.ssl is None or (options.ssl != 'wildcard' and options.ssl != 'split'):
    j.console.warning('missing ssl method: wildcard, split')
    j.application.stop(1)

# settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
domain = settings.getStr('instance.ovc.domain')

# settings ssl keys
ssl = {'root': '', 'ovs': '', 'defense': '', 'novnc': ''}

if options.ssl == 'wildcard':
    ssl['root'] = domain
    ssl['ovs'] = domain
    ssl['defense'] = domain
    ssl['novnc'] = domain

if options.ssl == 'split':
    ssl['root'] = '%s.%s' % (environment, domain)
    ssl['ovs'] = 'ovs-%s.%s' % (environment, domain)
    ssl['defense'] = 'defense-%s.%s' % (environment, domain)
    ssl['novnc'] = 'novnc-%s.%s' % (environment, domain)

data = {
    'instance.publicip.gateway': options.gateway,
    'instance.publicip.start': options.ipstart,
    'instance.publicip.end': options.ipend,
    'instance.publicip.netmask': options.netmask,

    'instance.param.override': True,
    'instance.param.quiet': False,
    'instance.param.repo.path': repopath,

    'instance.master.rootpasswd': settings.getStr('instance.ovc.password'),
    'instance.param.main.host': environment,
    'instance.param.domain': settings.getStr('instance.ovc.domain'),

    'instance.host': 'auto',

    'instance.bootstrapp.ipadress': settings.getStr('instance.ovc.bootstrap.host'),
    'instance.bootstrapp.port': settings.getStr('instance.ovc.bootstrap.port'),

    # Servers name
    'instance.dcpm.servername': 'auto',
    'instance.bootstrapp.servername': 'auto',
    'instance.ovs.servername': 'auto',
    'instance.defense.servername': 'auto',
    'instance.novnc.servername': 'auto',
    'instance.grafana.servername': 'auto',

    # ssl keys
    'instance.ssl.root': ssl['root'],
    'instance.ssl.ovs': ssl['ovs'],
    'instance.ssl.defense': ssl['defense'],
    'instance.ssl.novnc': ssl['novnc'],

    'instance.smtp.login': 'support@mothership1.com',
    'instance.smtp.passwd': 'j-9uNv3a9BwYP6dTjYiuUw',
    'instance.smtp.port': '587',
    'instance.smtp.sender': 'support@greenitglobe.com',
    'instance.smtp.server': 'smtp.mandrillapp.com',

    'instance.grid.id': options.gid,
    'instance.reflector.root.passphrase': settings.getStr('instance.ovc.password'),
}

j.console.info('============================')
j.console.info('configuring machines')
j.console.info('============================')

setupService = j.atyourservice.new(name='ovc_configure_aio', instance='main', args=data)
setupService.install(reinstall=True)

j.console.success('machines configured')
