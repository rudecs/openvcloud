from JumpScale import j
from ovs.extensions.db.arakoon.ArakoonInstaller import ArakoonInstaller
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--cluster", dest="cluster", help="cluster name")
parser.add_option("-i", "--address", dest="address", help="ip address")
(options, args) = parser.parse_args()

if options.cluster is None:
	print '[-] missing cluster name'
	j.application.stop()

if options.address is None:
	print '[-] missing address'
	j.application.stop()

ArakoonInstaller.restart_cluster(options.cluster, options.address)
