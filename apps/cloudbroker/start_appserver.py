#this must be in the beginning so things are patched before ever imported by other libraries
from gevent import monkey
#monkey.patch_all()
monkey.patch_socket()
monkey.patch_thread()
monkey.patch_time()

from JumpScale import j
j.application.start('cloudbroker')
import JumpScale.portal

j.application.initGrid()
server = j.core.portal.getServer()
j.apps.cloud.cloudbroker # preload actor
server.start()
j.application.stop()
