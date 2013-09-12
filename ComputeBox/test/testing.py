from fabric.api import run

def startall():
	run('/etc/init.d/elasticsearch restart')
	run('cd /opt/jumpscale/apps/osis; python osisServerStart.py', pty=False)
	run('cd /opt/jumpscale/apps/cloudbroker; python start_appserver.py', pty=False)