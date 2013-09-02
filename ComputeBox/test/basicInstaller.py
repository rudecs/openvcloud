from fabric.api import run, put

def install_prereqs():
    run('apt-get install python2.7 dialog nginx curl mc ssh mercurial python-gevent python-simplejson python-numpy byobu python-apt ipython python-pip python-imaging python-requests python-paramiko gcc g++ python-dev python-zmq msgpack-python python-mhash python-libvirt wget -y')
    run('yes w | pip install urllib3 ujson blosc pycrypto pylzma')
    run('apt-get update')
    run('apt-get install mercurial ssh python2.7 python-apt openssl ca-certificates -y')
    run('mkdir -p /home/ISO')
    run('wget -P /home/ISO/ http://files.incubaid.com/iaas/ubuntu-13.04-server-amd64.iso')
    put('libvirt_no_sparse.patch', '/usr/share/pyshared/')
    put('raring.patch', '/tmp/')
    run('python /opt/jumpscale/shellcmds/jpackage_install --package installEnv')
    
