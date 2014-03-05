from JumpScale import j
j.application.start('cloudbroker')
import JumpScale.portal

server = j.core.portal.getServer()
j.apps.cloud.cloudbroker # preload actor
server.start()
j.application.stop()
