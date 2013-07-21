import time
from OpenWizzy import o
import OpenWizzy.portal

o.application.appname = "appserver6_test"
o.application.start()


o.manage.portal.startprocess()
    

o.application.stop()
