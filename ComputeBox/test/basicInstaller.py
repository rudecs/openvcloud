from fabric.api import run, put

def install_prereqs():
    run('apt-get install python2.7 dialog nginx curl mc ssh mercurial python-gevent python-simplejson python-numpy byobu python-apt ipython python-pip python-imaging python-requests python-paramiko gcc g++ python-dev python-zmq msgpack-python python-mhash python-libvirt -y')
    run('yes w | pip install urllib3 ujson blosc pycrypto pylzma')
    run('apt-get update')
    run('apt-get install mercurial ssh python2.7 python-apt openssl ca-certificates -y')
    run('mkdir -p /home/ISO')
    run('echo "ALL : 10.101.190.1 : allow" >> /etc/hosts.allow')
    run('echo "R00t3r" | scp -o StrictHostKeyChecking=no root@10.101.190.1:/home/ISO/ubuntu-13.04-server-amd64.iso /home/ISO/')
    put('libvirt_no_sparse.patch', '/usr/share/pyshared/')
    put('raring.patch', '/tmp/')
    run('python /opt/jumpscale/shellcmds/jpackage_install --package installEnv')
    
