from JumpScale import j
descr = """
check status of alertservice
"""

organization = 'cloudscalers'
author = "khamisr@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['storagenode']
period = 60 * 30 # 30min
enable = True
async = True
queue = 'process'
log = True

def action():
    ovsresults = list()
    ovscmds = {'OK': 'initctl list | grep ovs | grep start/running | sort',
           'HALTED': 'initctl list | grep ovs | grep -v start/running | sort'}
    for state, cmd in ovscmds.items():
        exitcode, results = j.system.process.execute(cmd, outputToStdout=True)
        if exitcode == 0:
            for result in results.splitlines():
                ovsresults.append({'message': result.split(' ')[0], 'category': 'OVS Services', 'state': state})
        else:
            ovsresults.append({'message': '', 'category': 'OVS Services', 'state': 'UNKNOWN'})


    import apt
    caches = apt.Cache()
    ovspackages = [cache for cache in caches if cache.name.startswith('openvstorage')]
    ovspackages.append(caches['alba'] if caches.has_key('alba') else None)

    for pkg in ovspackages:
        if pkg.is_installed:
            state = 'OK'
            version = pkg.installed.version
        else:
            state = 'ERROR'
            version = 'N/A'
        ovsresults.append({'message': '*Name:* %s. *Version:* %s' % (pkg.name, version), 'category': 'OVS Packages', 'state': state})

    return ovsresults
    

if __name__ == '__main__':
    print action()
