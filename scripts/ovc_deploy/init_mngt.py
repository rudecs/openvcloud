from JumpScale import j
"""
create GIT_VM
    clone OVC_GIT
    ays install -n bootstrapp
"""


def checkRequiredAys(location, cloudspace, login, passwd):
    data = {
        'instance.param.disk': 0,
        'instance.param.mem': 100,
        'instance.param.passwd': '',
        'instance.param.port': 9999,
        'instance.param.unixsocket': 0,
    }
    redis = j.atyourservice.new(name='redis', instance='system', args=data)
    redis.install(deps=True)

    data = {
        'instance.param.location': location,
        'instance.param.cloudspace': cloudspace,
        'instance.param.login': login,
        'instance.param.passwd': passwd
    }
    ms1 = j.atyourservice.new(name='ms1_client', args=data)
    ms1.install(deps=True)
    return ms1


def createMS1VM(name, memsize=0.5, ssdsize=10, installJS=True):
    """
    create a new mv on ms1
    name, str : name of the vm and instance name of the service node.ms1 created
    sshkey, str : instance name of the sshkey service to use to connect to the vm
    """
    data = {'instance.key.priv': ''}
    sshkey = j.atyourservice.new(name='sshkey', instance=name, args=data)
    sshkey.install()

    data = {
        'instance.param.ms1.connection': 'main',
        'instance.param.name': name,
        'instance.param.memsize': memsize,
        'instance.param.ssdsize': ssdsize,
        'instance.param.imagename': 'ubuntu.14.04.x64',
        'instance.param.ssh.key': sshkey.instance,
        'instance.param.ssh.shell': '/bin/bash -l -c',
        'instance.param.jumpscale': installJS
    }
    vm = j.atyourservice.new(name='node.ms1', instance=name, args=data)
    vm.install()
    cl = vm.actions._getSSHClient(vm)
    cl.user_passwd('root', 'jsRooter', True)
    return vm


def createNodeSSH(cl, spacesecret,  name, port=22):
    vm = j.tools.ms1.getMachineObject(spacesecret, name)
    ip = vm['interfaces'][0]['ipAddress']
    # login = vm['accounts'][0]['login']
    login = 'root'
    # password = vm['accounts'][0]['password']
    password = 'jsRooter'
    shell = '/bin/bash -l -c'
    jumpscale = False

    # genereta sshkey service
    cl.sudo('cd /opt/ovc_git; ays install -n sshkey -i %s --data key.priv:""' % name)
    # generate node.ssh service
    args = "ip=%s#ssh.port=%s#login=%s#password=%s#sshkey=%s \
            #jumpscale=%s#ssh.shell=%s" % (ip, port, login, password, name.strip(), jumpscale, shell)
    cl.sudo('cd /opt/ovc_git; ays install -n node.ssh -i %s --data \'%s\'' % (name, args))


def doPortForward(vmName, spacePort, vmPort, ms1Client='main', protocol='tcp'):
    data = {
        'instance.param.ms1.connection':ms1_client,
        'instance.param.protocol': protocol,
        'instance.param.space.port': spacePort,
        'instance.param.vm.name': vmName,
        'instance.param.vm.port': vmPort
    }
    portForward = j.atyourservice.new(name='ms1_portforward', instance='%s_%s_%s' % (vmName, spacePort, vmPort), args=data)
    portForward.install(deps=True)


def setupGitVM(gitVM, repoURL):
    cl = gitVM.actions._getSSHClient(gitVM)
    if not cl.dir_exists('/opt/ovc_git'):
        cl.run('git clone https://git.aydo.com/openvcloudEnvironments/OVC_GIT_Tmpl.git /opt/ovc_git')
        cl.run('cd /opt/ovc_git; git remote set-url origin %s' % repoURL)
    return gitVM


if __name__ == '__main__':
    ms1Client = checkRequiredAys(
        location='eu1',
        cloudspace='ovc_deploy',
        login='christophe',
        passwd='OshotsAg5',
    )

    vmsData = [
        {
            'name': 'ovc_git',
            'sshkey': 'ovc_git',
            'memsize': 0.5,
            'ssdsize': 10,
            'installJS': True
        },
        {
            'name': 'ovc_master',
            'sshkey': 'ovc_master',
            'memsize': 4,
            'ssdsize': 40,
            'installJS': True
        },
        {
            'name': 'ovc_reflector',
            'sshkey': 'ovc_reflector',
            'memsize': 0.5,
            'ssdsize': 10,
            'installJS': True
        },
        {
            'name': 'ovc_proxy',
            'sshkey': 'ovc_proxy',
            'memsize': 0.5,
            'ssdsize': 10,
            'installJS': True
        }
    ]
    vms = {}
    # create all vm
    for data in vmsData:
        vms[data['name']] = createMS1VM(name=data['name'], memsize=data['memsize'],
                                        ssdsize=data['ssdsize'],
                                        installJS=data['installJS'])

    portForwardData = [
        {
            'instance.param.ms1.connection': 'main',
            'instance.param.vm.name': 'ovc_master',
            'instance.param.space.port': 4444,
            'instance.param.vm.port': 4444,
            'instance.param.protocol': 'tcp'
        },
        {
            'instance.param.ms1.connection': 'main',
            'instance.param.vm.name': 'ovc_reflector',
            'instance.param.space.port': 22,
            'instance.param.vm.port': 22,
            'instance.param.protocol': 'tcp'
        },
        {
            'instance.param.ms1.connection': 'main',
            'instance.param.vm.name': 'ovc_proxy',
            'instance.param.space.port': 80,
            'instance.param.vm.port': 80,
            'instance.param.protocol': 'tcp'
        },
        {
            'instance.param.ms1.connection': 'main',
            'instance.param.vm.name': 'ovc_proxy',
            'instance.param.space.port': 443,
            'instance.param.vm.port': 443,
            'instance.param.protocol': 'tcp'
    }]

    # create portforwarding
    for data in portForwardData:
        instance = '%s_%s_%s' % (data['instance.param.vm.name'], data['instance.param.vm.port'], data['instance.param.space.port'])
        pf = j.atyourservice.new(name='ms1_portforward', instance=instance, args=data)
        pf.install(deps=True)

    # create git vm
    setupGitVM(vms['ovc_git'], repoURL='https://git.aydo.com/openvcloudEnvironments/test.git')

    # create node.ssh service on the git vm
    gitcl = vms['ovc_git'].actions._getSSHClient(vms['ovc_git'])
    spacesecret = ms1Client.hrd.getStr('instance.param.secret')
    for name in ['ovc_master', 'ovc_proxy', 'ovc_reflector']:
        createNodeSSH(gitcl, spacesecret, name)

    # push install script on the git vm
    # rest of the installation need to happend from the git vm
    content = j.system.fs.fileGetContents('install_mngt.py')
    gitcl.file_write('/opt/ovc_git/install_mngt.py', content)
    # execute install script on git vm
    gitcl.sudo('cd /opt/ovc_git/; /usr/local/bin/jspython /opt/ovc_git/install_mngt.py')