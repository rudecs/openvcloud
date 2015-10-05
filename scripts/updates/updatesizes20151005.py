#see https://youtrack.incubaid.com/issue/CB-418
from JumpScale import j
ccl = j.clients.osis.getNamespace('cloudbroker')

# patch sizes in cloudbroker
disksizes = [10, 20, 50, 100, 250, 500, 1000, 2000]
for sizeid in ccl.size.list():
    size = ccl.size.get(sizeid)
    size.disks = disksizes
    ccl.size.set(size)


# recreate sizes in libvirt
lcl = j.clients.osis.getNamespace('libvirt')
sizecbs = [(512, 1),
         (1024, 1),
         (2048, 2),
         (4096, 2),
         (8192, 4),
         (16384, 8)]
lcl.size.deleteSearch({})
for i in disksizes:
    for sizecb in sizecbs:
        if lcl.size.search({'memory': sizecb[0], 'disk': i})[0]:
            continue
        size = dict()
        size['disk'] = i
        size['memory'] = sizecb[0]
        size['name'] = '%i-%i' % (sizecb[0], i)
        size['vcpus'] = sizecb[1]
        lcl.size.set(size)
