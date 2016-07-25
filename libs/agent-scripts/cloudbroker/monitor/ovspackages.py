from JumpScale import j
descr = """
get ovs packages
"""

organization = 'cloudscalers'
author = "khamisr@codescalers.com"
version = "1.0"
roles = ['storagedriver']
enable = True
async = True
queue = 'process'
log = True

def action():
    import apt

    ovsresults = {}
    caches = apt.Cache()
    ovspackages = [cache for cache in caches if cache.name.startswith('openvstorage')]
    if 'alba' in caches:
        ovspackages.append(caches['alba'])

    for pkg in ovspackages:
        if pkg.is_installed:
            version = pkg.installed.version
            ovsresults[pkg.name] = version

    return ovsresults
    

if __name__ == '__main__':
    print action()
