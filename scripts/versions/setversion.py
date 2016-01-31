from JumpScale import j
from optparse import OptionParser
import fnmatch
import os

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory", help="directory (ays repository) to scan")
parser.add_option("-o", "--repository", dest="repository", help="repository url (eg: git.aydo.com/0-complexity/openvcloud.git)")

parser.add_option("-b", "--branch", dest="branch", help="freeze to than branch name")
parser.add_option("-r", "--revision", dest="revision", help="freeze to that revision (commit)")
parser.add_option("-t", "--tag", dest="tag", help="freeze to that tag name")
(options, args) = parser.parse_args()

def getRepoInfo(url):
    domain, type_, account, repo, localpath, url = j.do.getGitRepoArgs(url)
    return type_, account.lower(), repo.rstrip('.git').lower()

def getServicesFiles(path):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, 'service.hrd'):
            matches.append(os.path.join(root, filename))

    return matches

def freeze(export, target):
    for key, value in target.iteritems():
        if export.get(key):
            print '[+]   discarding %s: %s' % (key, export[key])
            export.pop(key)

        if value:
            print '[+]   setting %s: %s' % (key, value)
            export[key] = value

    return export

# options check
if not options.directory:
    print '[-] missing directory'
    j.application.stop()

if not options.repository:
    print '[-] missing repository'
    j.application.stop()

if not options.branch and not options.revision and not options.tag:
    print '[-] missing target (branch, revision or tag)'
    j.application.stop()

directory = options.directory
services = getServicesFiles(directory)
repoinfo = getRepoInfo(options.repository)

target = {
        'branch': options.branch,
        'revision': options.revision,
        'tag': options.tag
        }

for service in services:
    print '[+] updating: %s' % service
    hrd = j.core.hrd.get(service)
    exports = hrd.getDictFromPrefix('git.export')

    for index in exports:
        export = exports[index]
        if getRepoInfo(export['url']) == repoinfo:
            export = freeze(export, target)
            hrd.set('git.export.%s' % index, export)
            hrd.save()

print '[+] repository updated: %s' % directory
