from JumpScale import j
j.application.start('cryptopaymentadmin')

import JumpScale.portal

j.core.portal.getServer().start()
    

j.application.stop()
