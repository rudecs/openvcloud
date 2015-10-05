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
sizecbs = [('10GB at SSD Speed, Unlimited Transfer - 7.5 USD/month', 512, 1),
         ('10GB at SSD Speed, Unlimited Transfer - 15 USD/month', 1024, 1),
         ('10GB at SSD Speed, Unlimited Transfer - 18 USD/month', 2048, 2),
         ('10GB at SSD Speed, Unlimited Transfer - 36 USD/month', 4096, 2),
         ('10GB at SSD Speed, Unlimited Transfer - 70 USD/month', 8192, 4),
         ('10GB at SSD Speed, Unlimited Transfer - 140 USD/month', 16384, 8)]
lcl.size.deleteSearch({})
for i in disksizes:
    for sizecb in sizecbs:
        if lcl.size.search({'memory': sizecb[1], 'disk': i})[0]:
            continue
        size = dict()
        size['disk'] = i
        size['memory'] = sizecb[1]
        size['name'] = '%i-%i' % (sizecb[1], i)
        size['vcpus'] = sizecb[2]
        lcl.size.set(size)
