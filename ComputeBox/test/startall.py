from JumpScale import j

import JumpScale.baselib.screen

screens=["appserver","osis"]
for item in ["byobu","screen"]:
    cmd="killall %s"%item
    j.system.process.execute(cmd,dieOnNonZeroExitCode=False)

j.system.platform.screen.createSession('JumpScale',screens)
cmd="/etc/init.d/elasticsearch restart"
j.system.process.execute(cmd)

#start osis
path=j.system.fs.joinPaths("/opt/jumpscale/apps","osis")
cmd="cd %s;python osisServerStart.py"%path
j.system.platform.screen.executeInScreen('JumpScale',"osis",cmd,wait=1)

#start broker
pathb=j.system.fs.joinPaths("/opt/jumpscale/apps","cloudbroker")
cmd="cd %s;python start_appserver.py"%pathb
j.system.platform.screen.executeInScreen('JumpScale',"appserver",cmd,wait=1)