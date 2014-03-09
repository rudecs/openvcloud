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

def templates():
    run('jpackage install --name image_ubuntu1310 --domain cloudscalers')
    run('jpackage install --name image_fedora20 --domain cloudscalers')

def demodata():
    pythoncode = '''
from JumpScale import j
import JumpScale.grid.osis
import JumpScale.portal
j.core.portal.getClient('127.0.0.1', 9999, '1234') #lazy load actors
cl = j.core.osis.getClient(user='root')
ccl = j.core.osis.getClientForCategory(cl, 'cloudbroker', 'stack')
stack = ccl.new()
stack.apiUrl = 'qemu+ssh://%(host)s/system'
stack.descr = 'Libvirt Stack'
stack.type = 'LIBVIRT'
stack.name ='vScalers demo'
stack.referenceId = j.application.config.get('cloudscalers.compute.nodeid')
ccl.set(stack)
j.apps.cloud.cloudbroker.updateImages()
j.apps.cloudapi.accounts.create('demo_account', 'admin')
j.apps.cloudapi.cloudspaces.create(1, 'demo_space', 'admin')
    ''' % env
    run('python -c "%s"' % pythoncode)
