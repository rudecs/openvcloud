from fabric.api import run, put, reboot
import os

def install_compute_node(hostname, workspace):
    # install prerequisites
    run('apt-get update')
    run('apt-get install python-pip python2.7 python-dev ssh mercurial ipython -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    
    #Update sources.cfg and bitbucket.cfg
    run('mkdir -p /opt/jumpscale/cfg/jpackages')
    put(os.path.join(workspace, 'ComputeBox/test/sources.cfg'), '/opt/jumpscale/cfg/jpackages/')
    
    run('mkdir -p /opt/jumpscale/cfg/jsconfig')
    put(os.path.join(workspace, 'ComputeBox/test/bitbucket.cfg'), '/opt/jumpscale/cfg/jsconfig/')

    run('jpackage_update')

    run('jpackage_install --name compute_os_base')

    reboot(wait=300)

    put(os.path.join(workspace, 'ComputeBox/test/configurations/',hostname,'cloudscalers_compute_1.0.hrd'), '/opt/jumpscale/cfg/hrd/cloudscalers_compute_1.0.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/grid.hrd'), '/opt/jumpscale/cfg/hrd/grid.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/system_root_credentials.hrd'), '/opt/jumpscale/cfg/hrd/system_root_credentials.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/', hostname, 'elasticsearch.hrd'), '/opt/jumpscale/cfg/hrd/elasticsearch.hrd')

    #install core first since computenode configure is not run in seperate context
    run('jpackage_install --name grid')

    run('jpackage_install --name computenode')
    print 'Installed the compute node! Start installing cloudbroker'
    run('jpackage_install --name cloudbroker')

    put(os.path.join(workspace, 'ComputeBox/test/configurations/cloudscalers_frontend.hrd'), '/opt/jumpscale/cfg/hrd/cloudscalers_frontend.hrd')
    run('jpackage_install --name cloudscalers_fe')

    run('apt-get install screen byobu -y')
    put(os.path.join(workspace, 'ComputeBox/test/startall.py'), '/tmp/')
    run('python /tmp/startall.py')
