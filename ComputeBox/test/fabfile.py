from fabric.api import run

def install_jumpscale_core():
    run('pip install https://bitbucket.org/jumpscale/jumpscale_core/get/default.zip')
    
