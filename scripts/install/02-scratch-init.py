from JumpScale import j
from optparse import OptionParser
from optparse import OptionGroup
import random
import string

parser = OptionParser()
group = OptionGroup(parser, "global options")
parser.add_option("-b", "--backend", dest="backend", help="backend: ms1, docker")
parser.add_option("-G", "--git-user", dest="gituser", help="gitlab username")
parser.add_option("-P", "--git-pass", dest="gitpass", help="gitlab password")
parser.add_option("-e", "--environment", dest="environment", help="environment name (eg: be-test-1)")
parser.add_option("-d", "--domain", dest="domain", help="domain name (default: demo.greenitglobe.com)")

group = OptionGroup(parser, "mothership1 backend")
group.add_option("-u", "--user", dest="user", help="api username")
group.add_option("-p", "--pass", dest="passwd", help="api password")
group.add_option("-c", "--cloudspace", dest="cloudspace", help="cloudspace name")
group.add_option("-l", "--location", dest="location", help="cloudspace location")
parser.add_option_group(group)

group = OptionGroup(parser, "mothership1 backend")
group.add_option("-r", "--remote", dest="remote", help="daemon remote ip")
group.add_option("-o", "--port", dest="port", help="daemon remote port")
group.add_option("-i", "--public", dest="public", help="public host ip address")
parser.add_option_group(group)
(options, args) = parser.parse_args()

targets = ['ms1', 'docker']

"""
Stage 1: options parsing: global settings
"""
# global settings
optlist = {
    'environment': options.environment,
}

for item in optlist:
    if optlist[item] == None:
        print '[-] missing global argument: %s' % item
        j.application.stop()

if options.gituser == None:
    print("[+] no git user given, github will be used")

if options.backend not in targets:
    print '[-] unknown or missing backend'
    j.application.stop()

domain = options.domain if options.domain else 'demo.greenitglobe.com'

"""
Stage 2: settings hardcoded values
"""
# Settings
if options.gituser == None:
    gitlink = 'git@github.com:gig-projects/env_%s' % options.environment

else:
    gitlink = 'https://git.aydo.com/openvcloudEnvironments/%s' % options.environment

choice     = string.ascii_letters + string.digits
vmpassword = ''.join(random.choice(choice) for _ in range(12))

print '[+] installing environement: %s' % options.environment
print '[+] master password generated: %s' % vmpassword
print '[+] domain name: %s' % domain


"""
Stage 3: initializer
"""
ovc = j.clients.openvcloud.get()
ovc.initLocalhost(gitlink, options.gituser, options.gitpass)

"""
Stage 4: options parsing: backend validator
"""
# mothership1
if options.backend == 'ms1':
    optlist = {
        'user': options.user,
        'pass': options.passwd,
        'cloudspace': options.cloudspace,
        'location': options.location
    }

    for item in optlist:
        if optlist[item] == None:
            print '[-] missing mothiership1 argument: %s' % item
            j.application.stop()

    machine = ovc.initMothership(options.user, options.passwd, options.location, options.cloudspace)
    machine['type'] = 'ms1'

# docker
if options.backend == 'docker':
    optlist = {
        'remote': options.remote,
        'port': options.port,
        'public': options.public,
    }

    for item in optlist:
        if optlist[item] == None:
            print '[-] missing docker argument: %s' % item
            j.application.stop()

    machine = ovc.initDocker(options.remote, options.port, options.public)
    machine['type'] = 'docker'


"""
Stage 5: installing stuff
"""
ovc.initAYSGitVM(machine, gitlink, options.gituser, options.gitpass,
                 vmpassword, domain, options.environment, delete=True)
