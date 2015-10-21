import sys
sys.path.append('/opt/OpenvStorage')

from ovs.lib.helpers.toolbox import Toolbox
for function in Toolbox.fetch_hooks('update', 'postupgrade'):
    function(SSHClient('127.0.0.1', username='root'))
