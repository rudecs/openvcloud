
from OpenWizzy import o

o.application.appname = "usercreation"
o.application.start()

o.system.fs.changeDir("../appserver6Base")

o.system.fs.removeDirTree(o.system.fs.joinPaths(o.dirs.varDir,"db","system"))

o.core.appserver6.loadActorsInProcess()
#client=o.core.appserver6.getAppserverClient("127.0.0.1",9999,"1234")
#usermanager=client.getActor("system","usermanager",instance=0)

usermanager=o.apps.system.usermanager

usermanager.usercreate("despiegk","1234","","all,admin","kristof@despiegeleer.com,kristof@incubaid.com",0)
usermanager.usercreate("desmedt","1234","","all,admin","kristof@despiegeleer.com,kristof@incubaid.com",0)
usermanager.usercreate("dewolft","1234","","all,admin","kristof@despiegeleer.com,kristof@incubaid.com",0)
usermanager.usercreate("guest","1234","","guest","kristof@incubaid.com",0)

print "users created, appserver reset"



o.application.stop()