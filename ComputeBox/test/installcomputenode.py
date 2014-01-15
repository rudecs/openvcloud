from fabric.api import run, put, reboot
import os

def install_compute_node(hostname, workspace, jumpscalebranch):
    # install prerequisites
    run('apt-get update')
    run('apt-get install python-pip python2.7 python-dev ssh mercurial ipython -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/%s.zip' % jumpscalebranch)
    
    #Update sources.cfg and bitbucket.cfg
    run('mkdir -p /opt/jumpscale/cfg/jpackages')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/',hostname,'sources.cfg'), '/opt/jumpscale/cfg/jpackages/')

    run('mkdir -p /opt/jumpscale/cfg/hrd/')
    
    run('mkdir -p /opt/jumpscale/cfg/jsconfig')
    put(os.path.join(workspace, 'ComputeBox/test/bitbucket.cfg'), '/opt/jumpscale/cfg/jsconfig/')

    run('jpackage mdupdate')

    run('jpackage install --name core')
    run('jpackage install --name grid_master')
    run('jpackage install --name compute_os_base')

    reboot(wait=300)
    run('apt-get update')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/',hostname,'cloudscalers_compute_1.0.hrd'), '/opt/jumpscale/cfg/hrd/cloudscalers_compute_1.0.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/',hostname, 'grid.hrd'), '/opt/jumpscale/cfg/hrd/grid.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/',hostname, 'grid_master.hrd'), '/opt/jumpscale/cfg/hrd/grid_master.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/system_root_credentials.hrd'), '/opt/jumpscale/cfg/hrd/system_root_credentials.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/', hostname, 'elasticsearch.hrd'), '/opt/jumpscale/cfg/hrd/elasticsearch.hrd')
    put(os.path.join(workspace, 'ComputeBox/test/configurations/agent.hrd'), '/opt/jumpscale/cfg/hrd/agent.hrd')

    run('jpackage install --name grid')

    run('jpackage install --name computenode')
    print 'Installed the compute node! Start installing cloudbroker'
    run('jpackage install -r --name cloudbroker')
    

    run('jpackage install --name logger')

    put(os.path.join(workspace, 'ComputeBox/test/configurations/cloudscalers_frontend.hrd'), '/opt/jumpscale/cfg/hrd/cloudscalers_frontend.hrd')
    run('jpackage install --name cloudscalers_fe')
    run('jsprocess_startAllReset')

