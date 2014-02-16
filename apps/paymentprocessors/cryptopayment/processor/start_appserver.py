from JumpScale import j
j.application.start('cryptopaymentprocessor')

import JumpScale.portal

j.manage.portal.startprocess()
    

j.application.stop()
