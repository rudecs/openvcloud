from fabric.api import run

def install_jumpscale_core():
    run('apt-get update')
    run('apt-get install python-pip -y')
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    
