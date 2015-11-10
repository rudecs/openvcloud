#!/usr/bin/env jspython

from JumpScale import j
import time
import urllib
import json


class State(object):

    def __init__(self):
        self._file = 'state.json'
        self.json = None

        if j.system.fs.exists(path=self._file):
            content = j.system.fs.fileGetContents(self._file)
            self.json = json.loads(content)
        else:
            self.json = {}

    def done(self, action, data):
        self.json[action] = data
        content = json.dumps(self.json, indent=4)
        j.system.fs.writeFile(filename=self._file,contents=content)

    def is_done(self, action):
        if action in self.json:
            return True, self.json[action]
        else:
            return False, None

    def reset(self):
        j.system.fs.remove(self._file)


class Vnas(object):

    def __init__(self, api_url):
        """
        api_url : url of the target environement e.g: du-conv-1.demo.greenitglobe.com
        """

        self.fronts = []
        self.stores = []
        self.ovc = j.tools.ms1.get(apiURL=api_url)
        self.spacesecret = None
        self.masterkey = None

    def _format_ays_cmd(self, action, service_name, service_instance='main', args={}, parent=''):
        """
        convert a dict into a valid ays '--data' string
        {'foor':'bar', 'hello': 'world'} => 'foo:bar hello:world'
        """
        out = 'ays %s -n %s -i %s' % (action, service_name, service_instance)
        if len(args) > 0:
            out += " --data "
            str_args = ''
            for k, v in args.iteritems():
                str_args += "%s:%s " % (k, v)
            out += " '%s' " % str_args
        if parent != '':
            out += ' --parent %s' % parent
        return out

    def get_passwd_vm(self, vm_name):
        obj = self.ovc.getMachineObject(self.spacesecret, vm_name)
        return obj['accounts'][0]['password']

    def enable_multiverse(self, cl):
        cl.file_append('/etc/apt/sources.list', '\ndeb http://archive.ubuntu.com/ubuntu trusty multiverse')
        cl.package_update()

    def add_ovc_domain(self, cl):
        cl.file_append('/opt/jumpscale7/hrd/system/atyourservice.hrd', """
            metadata.openvcloud            =
    branch:'master',
    url:'https://git.aydo.com/0-complexity/openvcloud_ays',
    """)

    def install_js(self, cl):
        cl.run('curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh')

    def set_git_credentials(self, cl, login='awesomo', passwd='jsR00t3r'):
        cl.run('jsconfig hrdset -n whoami.git.login -v "%s"' % login)
        cl.run('jsconfig hrdset -n whoami.git.passwd -v "%s"' % passwd)

    def config_vm(self, cl):
        self.enable_multiverse(cl)
        self.install_js(cl)
        self.set_git_credentials(cl)
        self.add_ovc_domain(cl)

    def installPersTest(self, cl):
        # required for the perf tests
        cl.package_install('python-pip')
        cl.package_install('python-dev')
        cl.run('pip install paramiko_gevent')

    def isConnected(self):
        if self.spacesecret is None:
            print "you need to connect first. please use the 'connect' method"
            return False
        return True

    def get_ssh_key(self):
        if not j.system.fs.exists(path='/root/.ssh/id_rsa'):
            j.system.platform.ubuntu.generateLocalSSHKeyPair()
        key = j.system.fs.fileGetContents('/root/.ssh/id_rsa')
        keypub = j.system.fs.fileGetContents('/root/.ssh/id_rsa.pub')
        return (key, keypub)

    def create_vm(self, name, memsize=2, ssdsize=10, stack_id=None, disks=[]):
        if not self.isConnected():
            return
        _, key = self.get_ssh_key()
        id, ip, port = self.ovc.createMachine(self.spacesecret, name, memsize=memsize, ssdsize=ssdsize, imagename='Ubuntu 14.04 x64', delete=True, sshkey=key, stackId=stack_id, disks=disks)
        obj = self.ovc.getMachineObject(self.spacesecret, name)
        return ip, port, obj['accounts'][0]['password']

    def connect(self, username, password, cloudspace, location='dev'):
        """
        username : username of yout account on the environement
        password : password of yout account on the environement
        """
        self.spacesecret = self.ovc.getCloudspaceSecret(username, password, cloudspace, location)

    def ssh_to_vm(self, ip, port=22, login='cloudscalers', passwd=None, ssh_key='/root/.ssh/id_rsa'):
        cl = j.remote.cuisine.connect(ip, port, login=login, passwd=passwd)
        cl.fabric.api.env['key_filename'] = ssh_key
        cl.fabric.api.env['user'] = login
        cl.mode_sudo()
        return cl

    def delete_all_vm(self):
        for obj in self.ovc.listMachinesInSpace(self.spacesecret):
            self.ovc.deleteMachine(self.spacesecret, obj['name'])
    
    def allow_masterkey(self, remote):
        if self.masterkey is not None:
            remote.run("echo '%s' >> /root/.ssh/authorized_keys" % self.masterkey)
        else:
            print '[-] master key not set'

    def create_master(self):
        vmName = 'master'
        ip, port, passwd = self.create_vm(vmName)
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)
        data = {
            'instance.param.rootpasswd': 'rooter',
            'instance.ip': ip,
        }
        cmd = self._format_ays_cmd('install', 'vnas_master', 'main', data)
        print "[+] execute %s" % (cmd)
        cl.run(cmd)
        cl.package_install('iozone3')
        
        # building own ssh key
        cl.ssh_keygen('root', 'rsa')
        
        # allow himself
        self.masterkey = cl.run("cat /root/.ssh/id_rsa.pub")
        print self.masterkey
        
        cl.run("cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys")

        obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        print obj['interfaces'][0]
        
        return {'ip': obj['interfaces'][0]['ipAddress'], 'port': obj['interfaces'][0]['ipAddress']}

    # def createAD(self, serviceObj):
    def create_AD(self):
        print '[+] create active directory VM'
        ip, port, passwd = self.create_vm('vnas_ad')

        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)

        cmd = self._format_ays_cmd('install', 'vnas_ad', 'main')
        print "[+] execute %s" % (cmd)
        cl.run(cmd)
        
        self.allow_masterkey(cl)

        obj = self.ovc.getMachineObject(self.spacesecret, 'vnas_ad')
        return obj['interfaces'][0]['ipAddress']

    def create_backend(self, id, stack_id, master_ip, nid, nbr_disk=10):
        vmName = 'vnas_backend%s' % id

        ip, port, passwd = self.create_vm(vmName,  memsize=4, stack_id=stack_id, disks=[2000 for _ in range(nbr_disk)])
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)

        data = {
            'instance.stor.id': id,
            'instance.stor.export.dir': '/mnt/disks',
            'instance.disk.number': nbr_disk,
            'instance.disk.size': 2000,
            'instance.master.address': master_ip,
            'instance.agent.nid': nid,
        }
        cmd = self._format_ays_cmd('install', 'vnas_stor', str(id), data)
        print "[+] execute %s" % (cmd)
        cl.run(cmd)

        for i in range(nbr_disk):
            data = {
                'instance.disk.id': i,
                'instance.nfs.host': '192.168.103.0/24',
                'instance.nfs.options': 'rw,no_root_squash,no_subtree_check',
            }
            cmd = self._format_ays_cmd('install', 'vnas_stor_disk', str(i), data)
            print "[+] execute %s" % (cmd)
            cl.run(cmd)

        # make sure nfs server is running
        cl.run('/etc/init.d/nfs-kernel-server restart')
        cl.package_install('iozone3')
        
        self.allow_masterkey(cl)

        obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        ip = obj['interfaces'][0]['ipAddress']

        return {'addr': ip, 'id': id + 1}

    def create_frontend(self, id, stack_id, ad_ip, master_ip, nid, stores):
        vmName = 'vnas_frontend%s' % id
        ip, port, passwd = self.create_vm(vmName,  memsize=4, stack_id=stack_id)
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)

        data = {
            'instance.member.ad.address': ad_ip,
            'instance.member.address': ip,
            'instance.master.address': master_ip,
            'instance.agent.nid': nid,
            'instance.vnas.refresh': 10,  # TODO allow configuration of this value ??
            'instance.vnas.blocksize': 16777216,
            'instance.vnas.timeout': 10,  # FIXME ?
            'instance.param.timeout': 10, # FIXME ?
        }
        for store in stores:
            data['instance.stores.%s' % store['id']] = store['addr']
        
        self.allow_masterkey(cl)

        cmd = self._format_ays_cmd('install', 'vnas_node', str(id), data)
        print "[+] execute %s" % (cmd)
        cl.run(cmd)
        cl.package_install('iozone3')
        
        obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        ip = obj['interfaces'][0]['ipAddress']

        return {'addr': ip, 'id': id + 1}
    
    def populate(self, master, port, ad, backends, frontends):
        # grab ip of vm
        # install service on master
        # set hosts
        
        print master
        print ad
        print backends
        print frontends
        
        cl = self.ssh_to_vm(master, port=port)
        cl.run('ls')
        
        return True

if __name__ == '__main__':

    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    commands = ['deploy', 'remove']
    parser.add_argument("action", choices=commands, help='Command to perform\n')
    parser.add_argument('--api', required=True, help='url of the environement api. (du-conv-1.demo.greenitglobe.com)')
    parser.add_argument('-l', '--login', required=True, help='account name')
    parser.add_argument('-p', '--password', required=True, help='password')
    parser.add_argument('-cs', '--cloudspace', required=True, help='cloudspace name')
    parser.add_argument('-loc', '--location', required=True, help='location')

    args = parser.parse_args()

    vnas = Vnas(args.api)
    vnas.connect(args.login, args.password, args.cloudspace, args.location)
    state = State()

    if args.action == 'deploy':

        master_ip = None
        ok, stuff = state.is_done('master')
        if not ok:
            stuff = vnas.create_master()
            master_ip = stuff['ip']
            master_port = stuff['port']
            state.done('master', {'ip': master_ip, 'key': vnas.masterkey, 'port': master_port})
            
        else:
            master_ip = stuff['ip']
            master_port = stuff['port']
            vnas.masterkey = stuff['key']
            print '[+] master key loaded: %s' % vnas.masterkey

        ad_ip = None
        ok, ad_ip = state.is_done('ad')
        if not ok:
            ad_ip = vnas.create_AD()
            state.done('ad', ad_ip)

        backends = []
        for i in range(1, 5):
            ok, store = state.is_done('backend%s' % i)
            if not ok:
                store = vnas.create_backend(i, i, master_ip, i, nbr_disk=10)
                state.done('backend%s' % i, store)

            backends.append(store)

        frontends = []
        for i in range(2):
            ok, _ = state.is_done('frontend%s' % i)
            if not ok:
                store = vnas.create_frontend(i, i+1, ad_ip, master_ip, i+1, backends)
                state.done('frontend%s' % i, store)
            
            frontends.append(store)
        
        # save stuff
        vnas.populate(master_ip, master_port, ad_ip, backends, frontends)

    elif args.action == 'remove':
        vnas.delete_all_vm()
        state.reset()
