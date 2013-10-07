from fabric.api import run

def bootstrap():
    run('jpackage_update')
    run('jpackage_install --name demo --domain cloudscalers --version 1.0')