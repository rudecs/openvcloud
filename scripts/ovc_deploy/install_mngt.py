from JumpScale import j


# def createNodeSSH(ip, port, login, password, installJS=False):
#     data = {'instance.key.priv': ''}
#     sshkey = j.atyourservice.new(name='sshkey', instance=name, args=data)
#     sshkey.install()

#     data = {
#         'instance.ip': ip,
#         'instance.ssh.port': port,
#         'instance.login': login,
#         'instance.password': password,
#         'instance.sshkey': sshkey.instance,
#         'instance.jumpscale': installJS,
#         'instance.ssh.shell': '/bin/bash -l -c'
#     }
#     vm = j.atyourservice.new(name='node.ssh', instance=name, args=data)
#     vm.install()
#     return vm


def setupReflector(reflectorVM, ovc_git='/opt/ovc_git'):
    cl = reflectorVM.actions._getSSHClient(reflectorVM)
    cl.user_ensure('guest', shell='/bin/bash')

    if not cl.file_exists('/root/.ssh/id_dsa'):
        cl.ssh_keygen('root')
        cl.run('cp /root/.ssh/id_dsa %s' % j.system.fs.joinPaths(ovc_git, 'keys/reflector_root_dsa'))
        cl.run('cp /root/.ssh/id_dsa.pub %s' % j.system.fs.joinPaths(ovc_git, 'keys/reflector_root_dsa.pub'))
    if not cl.file_exists('/home/guest/.ssh/id_dsa'):
        cl.ssh_keygen('guest')
        cl.run('cp /home/guest/.ssh/id_dsa %s' % j.system.fs.joinPaths(ovc_git, 'keys/reflector_guest_dsa'))
        cl.run('cp /home/guest/.ssh/id_dsa.pub %s' % j.system.fs.joinPaths(ovc_git, 'keys/reflector_guest_dsa.pub'))

    content = cl.file_read('/etc/ssh/sshd_config')
    if 'GatewayPorts yes' not in content:
        cl.file_append('/etc/ssh/sshd_config', '\nGatewayPorts yes')
        cl.run('restart ssh')
    cl.run('password -d root')


def setupProxy(proxyVM, host, masterIP, dcpmServerName, dcpmInternalHost,
               ovsServerName, defenseServerName, novncServerName):
    cl = proxyVM.actions._getSSHClient(proxyVM)
    cl.run('password -d root')

    data = {
        'instance.host': host,
        'instance.master.ipadress': masterIP,
        'instance.dcpm.servername': dcpmServerName,
        'instance.dcpm.internalhost': dcpmInternalHost,
        'instance.ovs.servername': ovsServerName,
        'instance.defense.servername': defenseServerName,
        'instance.novnc.servername': novncServerName
    }

    ssloffloader = j.atyourservice.new(name='ssloffloader', args=data, parent=proxyVM)
    ssloffloader.consume('node', proxyVM.instance)
    ssloffloader.install(deps=True)


def setupMaster(masterVM, masterPasswd, gateway, pubIPStart, pubIPEnd):
    cl = masterVM.actions._getSSHClient(masterVM)
    cl.run('password -d root')

    data = {
        'instance.param.rootpasswd': masterPasswd,
        'instance.param.publicip.gateway': gateway,
        'instance.param.publicip.netmask': '255.255.255.0',
        'instance.param.publicip.start': pubIPStart,
        'instance.param.publicip.end': pubIPEnd,
        'instance.param.dcpm.url': 'https://dcpmtest.demo.greenitglobe.com',
        'instance.param.ovs.url': 'https://ovstest.demo.greenitglobe.com',
        'instance.param.portal.url': 'https://test.demo.greenitglobe.com',
        'instance.param.oauth.url': 'https://test.demo.greenitglobe.com',
        'instance.param.defense.url': 'https://defensetest.demo.greenitglobe.com',
    }
    cb_master = j.atyourservice.new(name='cb_master_aio', args=data, parent=masterVM)
    cb_master.consume('node', masterVM.instance)
    cb_master.install(deps=True)


if __name__ == '__main__':
    vms = {}
    for name in ['ovc_master', 'ovc_reflector', 'ovc_proxy']:
        vms[name] = j.atyourservice.get(name='node.ssh', instance=name)

    # install reflector vm
    setupReflector(vms['ovc_reflector'], ovc_git='/opt/ovc_git')

    # install proxy vm
    spacesecret = ms1Client.hrd.get('instance.param.secret')
    details = j.tools.ms1.getMachineObject(spacesecret, 'ovc_master')
    masterIP = details['interfaces'][0]['ipAddress']
    setupProxy(vms['ovc_proxy'], host='test.demo.greenitglobe.com', masterIP=masterIP,
               dcpmServerName='dcpmtest.demo.greenitglobe.com',
               dcpmInternalHost='192.168.1.1',
               ovsServerName='ovstest.demo.greenitglobe.com',
               defenseServerName='defensetest.demo.greenitglobe.com',
               novncServerName='vnctest.demo.greenitglobe.com')

    # install master vm
    setupMaster(vms['ovc_master'], masterPasswd='rooter', gateway='192.168.103.1',
                pubIPStart='192.168.100.1', pubIPEnd='192.168.100.100')

    # share key between vms
    masterCL = vms['ovc_master'].actions._getSSHClient(vms['ovc_master'])
    reflectorCL = vms['ovc_reflector'].actions._getSSHClient(vms['ovc_reflector'])
    pub = reflectorCL.file_read('/home/guest/.ssh/id_dsa.pub')
    masterCL.ssh_authorize('root', pub)
