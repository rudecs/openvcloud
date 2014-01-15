from JumpScale import j
j.application.start('cloudbroker')
import JumpScale.portal

j.core.portal.getServer().start()
j.application.stop()
