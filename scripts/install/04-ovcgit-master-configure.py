from JumpScale import j
from argparse import ArgumentParser
import os
os.environ.pop('TMUX', None)  # allow install inside tmux

parser = ArgumentParser()
parser.add_argument("-G", "--gid", dest="gid", help="grid id", required=True, type=int)
parser.add_argument("-S", "--ssl", dest="ssl", help="set ssl keys method: wildcard or split", required=True)
parser.add_argument("-c", "--client_id", dest="client_id", help="Itsyouonline organization", required=True)
parser.add_argument("-cs", "--client_secret", dest="client_secret",
                    help="Itsyouonline organization api secret", required=True)
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
ssl = {'root': '', 'ovs': '', 'novnc': ''}

if options.ssl == 'wildcard':
    ssl['root'] = domain
    ssl['ovs'] = domain
    ssl['novnc'] = domain

if options.ssl == 'split':
    ssl['root'] = '%s.%s' % (environment, domain)
    ssl['ovs'] = 'ovs-%s.%s' % (environment, domain)
    ssl['novnc'] = 'novnc-%s.%s' % (environment, domain)

data = {
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
    'instance.novnc.servername': 'auto',
    'instance.grafana.servername': 'auto',

    # itsyouonline param
    'instance.itsyouonline.client_id': options.client_id,
    'instance.itsyouonline.client_secret': options.client_secret,

    # ssl keys
    'instance.ssl.root': ssl['root'],
    'instance.ssl.ovs': ssl['ovs'],
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
