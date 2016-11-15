from JumpScale import j
from argparse import ArgumentParser
import os
os.environ.pop('TMUX', None)  # allow install inside tmux

parser = ArgumentParser()
parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", help="supress ssh output", default=False)
parser.add_argument("-R", "--no-reflector", dest="noreflector", action="store_true", help="do not use reflector")
parser.add_argument("-r", "--reflector", dest="reflector", action="store_true", help="force reflector installation")
(options, args) = parser.parse_args()

if options.noreflector is None and options.reflector is None:
    clients = j.atyourservice.findServices(name='ms1_client', instance='main')
    options.noreflector = (len(clients) == 0)

settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')

repopath = settings.getStr('instance.ovc.path')

data = {
    'instance.param.override': True,
    'instance.param.quiet': options.quiet,
    'instance.param.repo.path': repopath,
    'instance.bootstrapp.port': settings.getStr('instance.ovc.bootstrap.port'),
    'instance.skip.reflector': options.noreflector,
}


j.console.info('============================')
j.console.info('spawning machines')
j.console.info('============================')

setupService = j.atyourservice.new(name='ovc_machines_aio', instance='main', args=data)
setupService.install(reinstall=True)

j.console.success('machines spawned')
