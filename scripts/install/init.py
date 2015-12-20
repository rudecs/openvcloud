from JumpScale import j

# Docker settings
usedocker  = False
dockerhost = '172.17.0.1'
dockerport = 2375

# Mothership1 credentials and data
usems1      = True
ms1username = ''
ms1password = ''
ms1location = 'eu1'
cloudspace  = 'testing'

# GitLab credentials and data
gitspace    = 'be-test-1'
gitusername = ''
gitpassword = ''

# Settings
gitlink     = 'https://git.aydo.com/openvcloudEnvironments/%s' % gitspace
vmpassword  = 'rooter'

print '[+] installing environement: %s' % gitspace
print '[+] mothership1 cloudspace : %s' % cloudspace

ovc = j.clients.openvcloud.get()

if usems1 and usedocker:
	print '[-] cannot use docker and mothership1 in the same time'
	j.application.stop()

if not usems1 and not usedocker:
	print '[-] no backend selected'
	j.application.stop()

if usems1:
	machine = ovc.initMothership(ms1username, ms1password, ms1location, cloudspace)

if usedocker:
	machine = ovc.initDocker(dockerhost, dockerport)

ovc.initAYSGitVM(machine, gitlink, gitusername, gitpassword, vmpassword, delete=True)

