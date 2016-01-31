from JumpScale import j
descr = """
get ovs packages
"""

organization = 'cloudscalers'
author = "khamisr@codescalers.com"
version = "1.0"
roles = ['storagenode']
enable = True
async = True
queue = 'process'
log = True

def action():
    import apt

    ovsresults = {}
    caches = apt.Cache()
    ovspackages = [cache for cache in caches if cache.name.startswith('openvstorage')]
    ovspackages.append(caches['alba'] if caches.has_key('alba') else None)

    for pkg in ovspackages:
        if pkg.is_installed:
            version = pkg.installed.version
            ovsresults[pkg.name] = version

    return ovsresults
    

if __name__ == '__main__':
    print action()
