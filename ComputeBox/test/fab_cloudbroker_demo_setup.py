from fabric.api import run

def bootstrap():
    run('jpackage_update')
    run('jpackage_install --name cloudbroker_minimal_install --domain cloudscalers --version 1.0')
