from JumpScale import grid
from JumpScale import j

cloudbroker = j.core.osis.getClientForNamespace('cloudbroker')
libvirt = j.core.osis.getClientForNamespace('libvirt')

osis_lsize = libvirt.size

sizecbs = [('10GB at SSD Speed, Unlimited Transfer - 7.5 USD/month', 512, 1),
           ('10GB at SSD Speed, Unlimited Transfer - 15 USD/month', 1024, 1),
           ('10GB at SSD Speed, Unlimited Transfer - 18 USD/month', 2048, 2),
           ('10GB at SSD Speed, Unlimited Transfer - 36 USD/month', 4096, 2),
           ('10GB at SSD Speed, Unlimited Transfer - 70 USD/month', 8192, 4),
           ('10GB at SSD Speed, Unlimited Transfer - 140 USD/month', 16384, 8)]


disksizes = [15,25,60,70,80,90,100]

for i in disksizes:
    for sizecb in sizecbs:
        size = dict()
        size['disk'] = i
        size['memory'] = sizecb[1]
        size['name'] = '%i-%i' % (sizecb[1], i) 
        size['vcpus'] = sizecb[2]
        osis_lsize.set(size)




