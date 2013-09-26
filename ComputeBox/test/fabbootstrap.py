from fabric.api import run, put
import os

def bootstrap():
	put(os.path.join(os.environ.get('WORKSPACE'), "ComputeBox/test/bootstrap_env.py"), "/tmp/")
	run('python /tmp/bootstrap_env.py')