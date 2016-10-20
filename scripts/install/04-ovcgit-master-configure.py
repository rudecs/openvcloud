from JumpScale import j
from optparse import OptionParser
import urllib
import os
os.environ.pop('TMUX', None)  # allow install inside tmux

""" FIXME: Move me """
def info(text):
    print '\033[1;36m[*] %s\033[0m' % text
    
def warning(text):
    print '\033[1;33m[-] %s\033[0m' % text

def success(text):
    print '\033[1;32m[+] %s\033[0m' % text

parser = OptionParser()
parser.add_option("-g", "--gateway", dest="gateway", help="gateway ip address")
parser.add_option("-s", "--start", dest="ipstart", help="public start ip address")
parser.add_option("-e", "--end", dest="ipend", help="public env ip address")
parser.add_option("-n", "--netmask", dest="netmask", help="public env ip netmask (default 255.255.255.0)")
parser.add_option("-G", "--gid", dest="gid", help="grid id")
parser.add_option("-S", "--ssl", dest="ssl", help="set ssl keys method: wildcard or split")
(options, args) = parser.parse_args()

# options
if options.gateway == None:
    print '[-] missing gateway address'
    j.application.stop()

if options.ipstart == None:
    print '[-] missing start public ip address'
    j.application.stop()

if options.ipend == None:
    print '[-] missing end public ip address'
    j.application.stop()

if options.gid == None:
    print '[-] missing grid id'
    j.application.stop()

if options.ssl == None or (options.ssl != 'wildcard' and options.ssl != 'split'):
    print '[-] missing ssl method: wildcard, split'
    j.application.stop()

if options.netmask == None:
    warning('netmask not set, using 255.255.255.0 as default value')
    options.netmask = '255.255.255.0'

# settings
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')

environment = settings.getStr('instance.ovc.environment')
repopath = settings.getStr('instance.ovc.path')
domain = settings.getStr('instance.ovc.domain')

# settings ssl keys
ssl = {'root': '', 'ovs': '', 'defense': '', 'novnc': ''}

if options.ssl == 'wildcard':
    ssl['root']    = domain
    ssl['ovs']     = domain
    ssl['defense'] = domain
    ssl['novnc']   = domain
    
if options.ssl == 'split':
    ssl['root']    = '%s.%s' % (environment, domain)
    ssl['ovs']     = 'ovs-%s.%s' % (environment, domain)
    ssl['defense'] = 'defense-%s.%s' % (environment, domain)
    ssl['novnc']   = 'novnc-%s.%s' % (environment, domain)

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
    
    # FIXME: dcpm part
    'instance.dcpm.ipadress': '192.168.103.252', # Note: not used later ? autodetected
    'instance.dcpm.port': 80,

    'instance.bootstrapp.ipadress': settings.getStr('instance.ovc.bootstrap.host'),
    'instance.bootstrapp.port': settings.getStr('instance.ovc.bootstrap.port'),

    # Servers name
    'instance.dcpm.servername': 'auto',
    'instance.bootstrapp.servername': 'auto',
    'instance.ovs.servername': 'auto',
    'instance.defense.servername': 'auto',
    'instance.novnc.servername': 'auto',
    'instance.grafana.servername': 'auto',
    'instance.safekeeper.servername': 'auto',
    
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

info('============================')
info('configuring machines')
info('============================')

setupService = j.atyourservice.new(name='ovc_configure_aio', instance='main', args=data)
setupService.install(reinstall=True)

success('machines configured')

