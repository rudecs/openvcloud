from fabric.api import run, put, reboot
import os

def install_jumpscale_core():
    run('apt-get update')
    run('apt-get install python-pip -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    run('apt-get install python2.7 python-dev ssh mercurial ipython -y')

    debians = ('linux-headers-3.11.0-5_3.11.0-5.10_all.deb', 'linux-headers-3.11.0-5-generic_3.11.0-5.10_amd64.deb', 'linux-image-3.11.0-5-generic_3.11.0-5.10_amd64.deb', 'linux-image-extra-3.11.0-5-generic_3.11.0-5.10_amd64.deb', 'linux-tools-common_3.11.0-5.10_all.deb', 'bcache-tools-1.0.0_1.0.0-1_all.deb')
    for deb in debians:
        run('wget -P /tmp/ http://files.incubaid.com/iaas/CloudScalers/%s' % deb)
        run('dpkg -i /tmp/%s' % deb)

    run('make-bcache -B /dev/sdb')
    run('make-bcache -C /dev/sdc')

    reboot(wait=300)

    WORKSPACE = os.environ.get('WORKSPACE')
    run('mkdir -p /opt/jumpscale/cfg/jpackages/')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/sources.cfg'), '/opt/jumpscale/cfg/jpackages/')
    put(os.path.join(WORKSPACE, 'ComputeBox/test/sources.cfg'), '/usr/local/lib/python2.7/dist-packages/JumpScale/core/_defaultcontent/cfg/jpackages/')


    run('mkdir -p ~/.ssh/')
    put(os.path.join(WORKSPACE, 'config/*'), '~/.ssh/')
    run('chmod 0600 ~/.ssh/*')
    run('mkdir -p /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('hg clone --ssh "ssh -o StrictHostKeyChecking=no" ssh://hg@bitbucket.org/incubaid/jp_cloudscalers /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('mv /opt/jumpscale/var/jpackages/metadata/cloudscalers/unstable/* /opt/jumpscale/var/jpackages/metadata/cloudscalers')
    run('mkdir -p /opt/jumpscale/var/jpackages/metadata/jpackagesbase')
    run('hg clone https://hg@bitbucket.org/jumpscale/jpackages_base /opt/jumpscale/var/jpackages/metadata/jpackagesbase/')
    run('mv /opt/jumpscale/var/jpackages/metadata/jpackagesbase/unstable/* /opt/jumpscale/var/jpackages/metadata/jpackagesbase')
    run('hg clone https://hg@bitbucket.org/jumpscale/jp_test /opt/jumpscale/var/jpackages/metadata/test/')
    run('mv /opt/jumpscale/var/jpackages/metadata/test/unstable/* /opt/jumpscale/var/jpackages/metadata/test')
    run('jpackage_install --name test_os')
    
    run('mkdir -p /home/ISO')
    run('wget -P /home/ISO/ http://files.incubaid.com/iaas/ubuntu-13.04-server-amd64.iso')

    run('jpackage_install --name test_compute')
    # run('jpackage_install --name bootstrapper')
    run('jpackage_install --name cloudbroker')
    run('jpackage_install --name cloudscalers_fe')

    put(os.path.join(WORKSPACE, 'ComputeBox/test/startall.py'), '/tmp/')
    run('python /tmp/startall.py')
