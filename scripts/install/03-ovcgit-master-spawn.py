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
parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="supress ssh output")
parser.add_option("-R", "--no-reflector", dest="noreflector", action="store_true", help="do not use reflector")
parser.add_option("-r", "--reflector", dest="reflector", action="store_true", help="force reflector installation")
(options, args) = parser.parse_args()

if options.quiet == None:
    options.quiet = False

if options.noreflector == None and options.reflector == None:
    clients = j.atyourservice.findServices(name='ms1_client', instance='main')
    options.noreflector = (len(clients) == 0)

if options.reflector:
    options.noreflector = False

settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')

repopath = settings.getStr('instance.ovc.path')

data = {
    'instance.param.override': True,
    'instance.param.quiet': options.quiet,
    'instance.param.repo.path': repopath,
    'instance.bootstrapp.port': settings.getStr('instance.ovc.bootstrap.port'),
    'instance.skip.reflector': options.noreflector,
}


info('============================')
info('spawning machines')
info('============================')

setupService = j.atyourservice.new(name='ovc_machines_aio', instance='main', args=data)
setupService.install(reinstall=True)

success('machines spawned')
