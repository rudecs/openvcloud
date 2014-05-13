from JumpScale import j
j.application.start('cloudbroker')
import JumpScale.portal

j.application.initGrid()
server = j.core.portal.getServer()
j.apps.cloud.cloudbroker # preload actor
server.start()
j.application.stop()
