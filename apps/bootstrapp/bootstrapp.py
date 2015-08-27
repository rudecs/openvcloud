from flask import Flask, request, make_response
from flask_restful import Resource, Api, abort

from JumpScale import j
from JumpScale.baselib import cmdutils

app = Flask(__name__)
api = Api(app)


class SSHMngr(object):
    """docstring for ConnectionMngr"""
    def __init__(self, hrd):
        self._config = hrd
        self._reflectorService = None

    def _getService(self, service):
        if j.system.fs.getcwd() != args.gitpath:
            j.system.fs.changeDir(args.gitpath)
        domain, name, instance = service.split('__')
        s = j.atyourservice.get(domain=domain, name=name, instance=instance)
        return s

    @property
    def reflector(self):
        if self._reflectorService is None:
            self._reflectorService = self._getService(self._config.getStr('instance.reflector.name'))
        return self._reflectorService


class bootstrap(Resource):
    def post(self):
        data = request.get_json()
        nodeKey = data['key.pub']
        hostname = data['hostname']
        login = data['login']
        remotePort = None

        try:
            remotePort = 21000 + int(hostname.strip('node'))
        except ValueError:
            return self.error(400, 'hostname should be something like node$nbr')

        try:
            # push pub key of node to reflector
            sshReflector = sshMngr.reflector.actions._getSSHClient(sshMngr.reflector)
            reflectorUser = hrd.getStr('instance.reflector.user')
            if not sshReflector.user_check(name=reflectorUser, need_passwd=False):
                sshReflector.user_ensure(reflectorUser)
            sshReflector.ssh_authorize(reflectorUser, nodeKey)
        except Exception as e:
            return self.error(500, 'Error during pushing of the public key to reflector: %s' % e.messaeg)


        masterKeyPath = j.system.fs.joinPaths(args.gitpath, 'keys/master_root')
        gitKeyPath = j.system.fs.joinPaths(args.gitpath, 'keys/git_root')
        if not j.system.fs.exists(path=masterKeyPath) or not j.system.fs.exists(path=gitKeyPath):
            j.atyourservice.remove(name='sshkey', instance=hostname)
            j.atyourservice.remove(name='node.ssh', instance=hostname)
            return self.error(500, 'public master or git key not available')

        masterPub = j.system.fs.fileGetContents(j.system.fs.joinPaths(args.gitpath, 'keys/master_root.pub'))
        gitPub = j.system.fs.fileGetContents(j.system.fs.joinPaths(args.gitpath, 'keys/git_root.pub'))
        gitPriv = j.system.fs.fileGetContents(j.system.fs.joinPaths(args.gitpath, 'keys/git_root'))

        try:
            # create sshkey to accces the new node
            data = {
                'instance.key.priv': gitPriv,
                'instance.key.pub': gitPub,
            }
            sshkey = j.atyourservice.new(name='sshkey', instance='nodes', args=data)
            sshkey.install(deps=True)

            data = {
                "instance.ip": hrd.getStr('instance.reflector.ip.priv'),
                "instance.ssh.port": remotePort,
                'instance.sshkey': sshkey.instance,
                'instance.login': login,
                'instance.password': "",
                'instance.jumpscale': False,
                'instance.ssh.shell': '/bin/bash -l -c'
            }
            node = j.atyourservice.new(name='node.ssh', instance=hostname, args=data)
            node.hrd  # force creation of service.hrd and action.py
        except Exception as e:
            j.atyourservice.remove(name='sshkey', instance=hostname)
            j.atyourservice.remove(name='node.ssh', instance=hostname)
            return self.error(500, 'error during creation of the node.ssh service: %s' % e.message)

        # prepare response
        resp = {
            'master.key': masterPub,
            'git.key': gitPub,
            'reflector.ip.priv': hrd.getStr('instance.reflector.ip.priv'),
            'reflector.ip.pub': hrd.getStr('instance.reflector.ip.pub'),
            'reflector.port': hrd.getStr('instance.reflector.port'),
            'reflector.user': hrd.getStr('instance.reflector.user'),
            'autossh.remote.port': remotePort,
            'autossh.node.port': 22,
        }
        # crete autossh service, but don't install, it will be installed by the node itself
        # when it gets the response
        data = {
            'instance.remote.bind': resp['reflector.ip.priv'],
            'instance.remote.address': resp['reflector.ip.pub'],
            'instance.remote.connection.port': resp['reflector.port'],
            'instance.remote.login': resp['reflector.user'],
            'instance.remote.port': resp['autossh.remote.port'],
            'instance.local.address': 'localhost',
            'instance.local.port': 22}
        autossh = j.atyourservice.new(name='autossh', instance=hostname, args=data)
        autossh.consume('node', node.instance)

        return resp

    def error(self, statusCode, message):
        abort(statusCode, message=message)

api.add_resource(bootstrap, '/')

args = None
sshMngr = None
hrd = None
if __name__ == '__main__':
    parser = cmdutils.ArgumentParser()
    parser.add_argument("--gitpath", default='/opt/code/OVC_GIT',
                        help='path to the OVC_GIT repo\n')
    parser.add_argument('--hrd', help='path to config hrd')
    args = parser.parse_args()

    if args.hrd is None:
        j.events.inputerror_critical('need to provice path to hrd, use --hrd')

    hrd = j.core.hrd.get(path=args.hrd, prefixWithName=False)
    sshMngr = SSHMngr(hrd)

    app.run(host='0.0.0.0', port=hrd.getInt('instance.listen.port'))
