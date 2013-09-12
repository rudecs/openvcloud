from fabric.api import put, run
import os

def startall():
	WORKSPACE = os.environ.get('WORKSPACE')
	put(os.path.join(WORKSPACE, 'ComputeBox/test/startall.py'), '/tmp/')
	run('python /tmp/startall.py')