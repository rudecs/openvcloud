from JumpScale import j
j.application.start('cryptopaymentprocessor')

import JumpScale.portal

j.core.portal.getServer().start()
    

j.application.stop()
