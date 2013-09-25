from fabric.api import run, put, reboot
import os

def install_jumpscale_core():
    # install prerequisites
    run('apt-get update')
    run('apt-get install python-pip python2.7 python-dev ssh mercurial ipython -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    
    #Update sources.cfg and bitbucket.cfg
    WORKSPACE = os.environ.get('WORKSPACE')
    
    run('mkdir -p /opt/jumpscale/cfg/jpackages')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/sources.cfg'), '/opt/jumpscale/cfg/jpackages/')
    
    run('mkdir -p /opt/jumpscale/cfg/jsconfig')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/bitbucket.cfg'), '/opt/jumpscale/cfg/jsconfig/')

    run('jpackage_update')

    run('mkdir -p /home/ISO')
    run('wget -P /home/ISO/ http://files.incubaid.com/iaas/ubuntu-13.04-server-amd64.iso')

    run('jpackage_install --name compute_os_base')

    reboot(wait=300)

    run('jpackage_install --name compute_kvm_base')

    put(os.path.join(WORKSPACE, 'ComputeBox/test/cloudscalers_compute_1.0.hrd'), '/opt/jumpscale/cfg/hrd/cloudscalers_compute_1.0.hrd')

    run('jpackage_install --name compute_configure')
    run('jpackage_install --name cloudbroker')
    run('jpackage_install --name cloudscalers_fe')

    run('apt-get install screen byobu -y')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/startall.py'), '/tmp/')
    run('python /tmp/startall.py')
