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


class Vnas(object):

    def __init__(self, api_url):
        """
        api_url : url of the target environement e.g: du-conv-1.demo.greenitglobe.com
        """

        self.fronts = []
        self.stores = []
        self.ovc = j.tools.ms1.get(apiURL=api_url)
        self.spacesecret = None

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
        # data = {'instance.key.priv': self.key}
        # keyService = j.atyourservice.new(name='sshkey', instance='vnas', args=data)
        # keyService.install()

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

    # def configure(self, serviceObj):


    #     j.actions.start(description='create vnas master', action=self.createMaster, actionArgs={'serviceObj': serviceObj}, category='vnas', name='vnas_master', serviceObj=serviceObj)

    #     j.actions.start(description='create vnas Active directory', action=self.createAD, actionArgs={'serviceObj': serviceObj}, category='vnas', name='vnas_ad', serviceObj=serviceObj)

    #     nid = 0
    #     nbrBackend = serviceObj.hrd.getInt('instance.nbr.stor')
    #     nbrDisk = serviceObj.hrd.getInt('instance.nbr.disk')
    #     for i in range(1, nbrBackend+1):
    #         id = i
    #         stack_id = 2+i
    #         nid += 1
    #         j.actions.start(description='create vnas stor %s' % i, action=self.createBackend, actionArgs={'id': id, 'stack_id': stack_id, 'nbrDisk': nbrDisk, 'masterSerivceObj': serviceObj, 'nid': nid}, category='vnas', name='vnas_stor %s' % i, serviceObj=serviceObj)

    #     nbrFrontend = serviceObj.hrd.getInt('instance.nbr.front')
    #     for i in range(1, nbrFrontend+1):
    #         id = i
    #         stack_id = 2+i
    #         nid += 1
    #         j.actions.start(description='create vnas frontend %s' % i, action=self.createFrontend, actionArgs={'id': id, 'stack_id': stack_id, 'masterSerivceObj': serviceObj, 'nid': nid}, category='vnas', name='vnas_node %s' % i, serviceObj=serviceObj)

        # schedule jobs into agentcontroller2
        # self.sheduleJobs(self.stores)

    def create_master(self):
        ip, port, passwd = self.create_vm('master')
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

        obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        return obj['interfaces'][0]['ipAddress']

    # def createAD(self, serviceObj):
    def create_AD(self):
        print '[+] create active directory VM'
        ip, port, passwd = self.create_vm('vnas_ad')
        # id, _, _ = self.ovc.createMachine(self.spacesecret, 'vnas_ad', memsize=2, ssdsize=10, imagename='Ubuntu 14.04 x64', delete=True, sshkey=self.keypub)
        # obj = self.ovc.getMachineObject(self.spacesecret, 'vnas_ad')
        # ip = obj['interfaces'][0]['ipAddress']
        # serviceObj.hrd.set('instance.ad.ip', ip)

        # data = {
        #     'instance.ip': ip,
        #     'instance.ssh.port': 22,
        #     'instance.login': 'root',
        #     'instance.password': '',
        #     'instance.sshkey': 'vnas',
        #     'instance.jumpscale': True,
        #     'instance.branch': '$(instance.branch)',
        #     'instance.ssh.shell': '/bin/bash -l -c'
        # }
        # j.atyourservice.remove(name='node.ssh', instance='vnas_ad')
        # nodeAD = j.atyourservice.new(name='node.ssh', instance='vnas_ad', args=data)
        # nodeAD.install(reinstall=True)
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)

        # allow SSH SAL to connect seamlessly
        # cl = nodeAD.actions.getSSHClient(nodeAD)
        # cl.ssh_keygen('root', keytype='rsa')
        # cl.run('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')
        # self.setGitCredentials(cl)
        cmd = self._format_ays_cmd('install', 'vnas_ad', 'main')
        print "[+] execute %s" % (cmd)
        cl.run(cmd)

        obj = self.ovc.getMachineObject(self.spacesecret, 'vnas_ad')
        return obj['interfaces'][0]['ipAddress']
        # vnasAD = j.atyourservice.new(name='vnas_ad', instance='main', args=data, parent=nodeAD)
        # vnasAD.consume('node', nodeAD.instance)
        # vnasAD.install(reinstall=True, deps=True)

    def create_backend(self, id, stack_id, master_ip, nid, nbr_disk=10):
        vmName = 'vnas_backend%s' % id

        ip, port, passwd = self.create_vm(vmName,  memsize=4, stack_id=stack_id, disks=[2000 for _ in range(nbr_disk)])
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)
        # self.ovc.createMachine(self.spacesecret, vmName, memsize=4, ssdsize=10, imagename='Ubuntu 14.04 x64', delete=True, sshkey=self.keypub)
        # obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        # ip = obj['interfaces'][0]['ipAddress']

        # self.stopVM(vmName)
        # for x in xrange(1, nbrDisk+1):
        #     diskName = 'data%s' % x
        #     self.ovc.addDisk(self.spacesecret, vmName, diskName, size=2000, description=None, type='D')
        # self.startVM(vmName)

        # if not j.system.net.waitConnectionTest(ip, 22, 120):
        #     j.events.opserror_critical(msg="VM didn't restart after we add disks to it", category="vnas_deploy")

        # data = {
        #     'instance.ip': ip,
        #     'instance.ssh.port': 22,
        #     'instance.login': 'root',
        #     'instance.password': '',
        #     'instance.sshkey': 'vnas',
        #     'instance.jumpscale': True,
        #     'instance.branch': '$(instance.branch)',
        #     'instance.ssh.shell': '/bin/bash -l -c'
        # }
        # j.atyourservice.remove(name='node.ssh', instance=vmName)
        # node = j.atyourservice.new(name='node.ssh', instance=vmName, args=data)
        # node.install(reinstall=True)

        # cl = node.actions.getSSHClient(node)
        # cl.ssh_keygen('root', keytype='rsa')
        # cl.run('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')
        # self.setGitCredentials(cl)

        # allow SSH SAL to connect seamlessly
        cl.ssh_keygen('root', keytype='rsa')
        cl.run('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')

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
        # vnasStor = j.atyourservice.new(name='vnas_stor', instance=str(id), args=data, parent=node)
        # vnasStor.consume('node', node.instance)
        # vnasStor.install(reinstall=True, deps=True)

        for i in range(nbr_disk):
            data = {
                'instance.disk.id': i,
                'instance.nfs.host': '192.168.103.0/24',
                'instance.nfs.options': 'rw,no_root_squash,no_subtree_check',
            }
            cmd = self._format_ays_cmd('install', 'vnas_stor_disk', str(i), data)
            print "[+] execute %s" % (cmd)
            cl.run(cmd)
            # stor_disk = j.atyourservice.new(name='vnas_stor_disk', instance="disk%s" % i, args=data, parent=vnasStor)
            # stor_disk.consume('node', node.instance)
            # stor_disk.install(deps=True)
        # make sure nfs server is running
        cl.run('/etc/init.d/nfs-kernel-server restart')
        cl.package_install('iozone3')

        obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        ip = obj['interfaces'][0]['ipAddress']

        return {'addr': ip, 'id': id+1}

    def create_frontend(self, id, stack_id, ad_ip, master_ip, nid, stores):
        vmName = 'vnas_frontend%s' % id
        ip, port, passwd = self.create_vm(vmName,  memsize=4, stack_id=stack_id)
        cl = self.ssh_to_vm(ip, port=port, passwd=passwd)
        self.config_vm(cl)

        # self.ovc.createMachine(self.spacesecret, vmName, memsize=2, ssdsize=10, imagename='Ubuntu 14.04 x64', delete=True, sshkey=self.keypub)
        # obj = self.ovc.getMachineObject(self.spacesecret, vmName)
        # ip = obj['interfaces'][0]['ipAddress']

        # data = {
        #     'instance.ip': ip,
        #     'instance.ssh.port': 22,
        #     'instance.login': 'root',
        #     'instance.password': '',
        #     'instance.sshkey': 'vnas',
        #     'instance.jumpscale': True,
        #     'instance.branch': '$(instance.branch)',
        #     'instance.ssh.shell': '/bin/bash -l -c'
        # }
        # j.atyourservice.remove(name='node.ssh', instance=vmName)
        # node = j.atyourservice.new(name='node.ssh', instance=vmName, args=data)
        # node.install(reinstall=True)

        # cl = node.actions.getSSHClient(node)
        # cl.ssh_keygen('root', keytype='rsa')
        # cl.run('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')
        # self.setGitCredentials(cl)

        data = {
            'instance.member.ad.address': ad_ip,
            'instance.member.address': ip,
            'instance.master.address': master_ip,
            'instance.agent.nid': nid,
            'instance.vnas.refresh': 5,  # TODO allow configuration of this value ??
            'instance.vnas.blocksize': 16777216,
        }
        for store in stores.iteritems():
            data['instance.stores.%s' % store['id']] = store['addr']

        cmd = self._format_ays_cmd('install', 'vnas_node', str(id), data)
        print "[+] execute %s" % (cmd)
        cl.run(cmd)
        cl.package_install('iozone3')
        # vnasNode = j.atyourservice.new(name='vnas_node', instance=str(id), args=data, parent=node)
        # vnasNode.consume('node', node.instance)
        # vnasNode.install(reinstall=True, deps=True)

    # def stopVM(self, vmName):
    #     for i in xrange(5):
    #         self.ovc.stopMachine(self.spacesecret, vmName)
    #         obj = self.ovc.getMachineObject(self.spacesecret, vmName)
    #         if obj['status'] == 'HALTED':
    #             return
    #         else:
    #             time.sleep(1.5)
    #     j.events.opserror_critical(msg="can't halt vm", category="vnas deploy")

    # def startVM(self, vmName):
    #     for i in xrange(5):
    #         self.ovc.startMachine(self.spacesecret, vmName)
    #         obj = self.ovc.getMachineObject(self.spacesecret, vmName)
    #         if obj['status'] == 'RUNNING':
    #             return
    #         else:
    #             time.sleep(1.5)
    #     j.events.opserror_critical(msg="can't start vm", category="vnas deploy")

    # def sheduleJobs(self, stores):
    #     cl = j.clients.ac.getByInstance('main')
    #     args = j.clients.ac.getRunArgs(domain='vnas', name='mount_vdisks', recurring_period=60, max_restart=3)
    #     data = {'stores': stores}
    #     job = cl.execute_jumpscript(None, None, 'vnas', 'mount_vdisks', args=args, role='vnas-backend')

if __name__ == '__main__':
    vnas = Vnas('du-conv-1.demo.greenitglobe.com')
    vnas.connect('christophe', 'jsR00t3r', 'vnas', 'dev')
    state = State()

    master_ip = None
    ok, master_ip = state.is_done('master')
    if not ok:
        master_ip = vnas.create_master()
        state.done('master', master_ip)

    ad_ip = None
    ok, ad_ip = state.is_done('ad')
    if not ok:
        ad_ip = vnas.create_AD()
        state.done('ad', ad_ip)

    backends = []
    for i in range(4):
        ok, store = state.is_done('backend%s' % i)
        if not ok:
            store = vnas.create_backend(i, i+1, master_ip, i+1, nbr_disk=10)
            state.done('backend%s' % i, store)
        backends.append(store)

    for i in range(2):
        ok, _ = state.is_done('frontend%s' % i)
        if not ok:
            vnas.create_frontend(i, i+1, ad_ip, master_ip, i+1, backends)
            state.done('frontend%s' % i, '')
