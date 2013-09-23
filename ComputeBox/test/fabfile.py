from fabric.api import run, put, reboot
import os

def install_jumpscale_core():
    # install prerequisites
    run('apt-get update')
    run('apt-get install python-pip -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    run('apt-get install python2.7 python-dev ssh mercurial ipython -y')

    # downlaod repos of packages
    WORKSPACE = os.environ.get('WORKSPACE')
    run('mkdir -p ~/.ssh/')
    put(os.path.join(WORKSPACE, 'config/*'), '~/.ssh/')
    run('chmod 0600 ~/.ssh/*')
    run('mkdir -p /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('hg clone --ssh "ssh -o StrictHostKeyChecking=no" ssh://hg@bitbucket.org/incubaid/jp_cloudscalers /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('mv /opt/jumpscale/var/jpackages/metadata/cloudscalers/unstable/* /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('mkdir -p /opt/jumpscale/var/jpackages/metadata/jpackagesbase')
    run('hg clone https://hg@bitbucket.org/jumpscale/jpackages_base /opt/jumpscale/var/jpackages/metadata/jpackagesbase/')
    run('mv /opt/jumpscale/var/jpackages/metadata/jpackagesbase/unstable/* /opt/jumpscale/var/jpackages/metadata/jpackagesbase')
    
    #Update sources.cfg to contain needed domains
    run('mkdir -p /opt/jumpscale/cfg/jpackages/')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/sources.cfg'), '/opt/jumpscale/cfg/jpackages/')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/sources.cfg'), '/usr/local/lib/python2.7/dist-packages/JumpScale/core/_defaultcontent/cfg/jpackages/')

    run('mkdir -p /home/ISO')
    run('wget -P /home/ISO/ http://files.incubaid.com/iaas/ubuntu-13.04-server-amd64.iso')

    run('jpackage_install --name compute_os_base')
    reboot(wait=300)

    run('jpackage_install --name compute_kvm_base')
    # run('export IPADDRESS="%s"' % )

    run('jpackage_install --name compute_configure')
    run('jpackage_install --name cloudbroker')
    run('jpackage_install --name cloudscalers_fe')

    run('apt-get install screen byobu -y')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/startall.py'), '/tmp/')
    run('python /tmp/startall.py')
