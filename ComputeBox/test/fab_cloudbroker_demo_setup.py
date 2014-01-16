from fabric.api import run, env, put
from StringIO import StringIO
def bootstrap():
    # write vncproxy hrd
    vncproxyhrd = """
vncproxy.libcloud.actor.host=127.0.0.1
vncproxy.libcloud.actor.port=9999
vncproxy.libcloud.actor.secret=1234
vncproxy.publicurl=http://%s:8091/vnc_auto.html?token=
    """ % env['host']
    put(StringIO(vncproxyhrd), '/opt/jumpscale/cfg/hrd/vncproxy.hrd')
    run('jpackage mdupdate')
    run('jpackage install --name cloudbroker_minimal_install --domain cloudscalers --version 1.0')
