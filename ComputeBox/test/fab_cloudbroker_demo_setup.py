from fabric.api import run, env, put
from StringIO import StringIO
def bootstrap():
    # write vncproxy hrd
    vncproxyhrd = """
vncproxy.libcloud.actor.host=127.0.0.1
vncproxy.libcloud.actor.port=80
vncproxy.libcloud.actor.secret=1234
vncproxy.publicurl=http://%s:8081/vnc_auto.html?token=
    """ % env['host']
    put(StringIO(vncproxyhrd), '/opt/jumpscale/cfg/hrd/vncproxy.hrg')
    run('jpackage_update')
    run('jpackage_install --name cloudbroker_minimal_install --domain cloudscalers --version 1.0')
