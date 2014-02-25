from JumpScale import j
j.application.start('billingengine')

import JumpScale.portal

j.core.portal.getServer().start()
    

j.application.stop()
