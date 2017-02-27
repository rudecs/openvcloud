PUBLICINPUT = '''\
# Allow dhcp client
in_port={port},priority=8000,dl_type=0x0800,nw_proto=0x11,tp_dst=67,dl_src={mac},idle_timeout=0,action=normal
# Allow arp req
in_port={port},priority=7000,dl_type=0x0806,dl_src={mac},arp_sha={mac},nw_src=0.0.0.0,idle_timeout=0,action=normal
# Drop DHCP server replies coming from here (rogue dhcp server)
in_port={port},priority=8000,dl_type=0x0800,nw_proto=0x11,tp_src=68,dl_src={mac},idle_timeout=0,action=drop
# Allow ARP responses.
in_port={port},priority=7000,dl_type=0x0806,dl_src={mac},arp_sha={mac},nw_src={publicipv4addr}/32,idle_timeout=0,action=normal
# Allow ipv4/mac (note: this is a /32) there can be only one (sic McLeod)
in_port={port},priority=6000,dl_type=0x0800,dl_src={mac},nw_src={publicipv4addr}/32,idle_timeout=0,action=normal
# # For Ipv6 we'll allow from the assigned subnet, but restrictive
# # Who'ze my Neighbour
# in_port={port},priority=8000,dl_src={mac},icmp6,ipv6_src={{{{ipv6prefix}}}}/64,icmp_type=135,nd_sll={mac},idle_timeout=0,action=normal
# # I am Neighbour
# in_port={port},priority=8000,dl_src={mac},icmp6,ipv6_src={{{{ipv6prefix}}}}/64,icmp_type=136,nd_target={{{{ipv6prefix}}}}/64,idle_timeout=0,action=normal
# # Standard ipv6 traffic (they can add 2^64 addresses to the pub iface, we don't care)
# in_port={port},priority=5000,dl_src={mac},ipv6_src={{{{ipv6prefix}}}}/64,icmp6,action=normal
# in_port={port},priority=5000,dl_src={mac},ipv6_src={{{{ipv6prefix}}}}/64,tcp6,action=normal
# in_port={port},priority=5000,dl_src={mac},ipv6_src={{{{ipv6prefix}}}}/64,udp6,action=normal
# Drop all other neighbour discovery.
in_port={port},priority=7000,icmp6,icmp_type=135,action=drop
in_port={port},priority=7000,icmp6,icmp_type=136,action=drop
# Drop other specific ICMPv6 types.
# Router advertisement.
in_port={port},priority=6000,icmp6,icmp_type=134,action=drop
# Redirect gateway.
in_port={port},priority=6000,icmp6,icmp_type=137,action=drop
# Mobile prefix solicitation.
in_port={port},priority=6000,icmp6,icmp_type=146,action=drop
# Mobile prefix advertisement.
in_port={port},priority=6000,icmp6,icmp_type=147,action=drop
# Multicast router advertisement.
in_port={port},priority=6000,icmp6,icmp_type=151,action=drop
# Multicast router solicitation.
in_port={port},priority=6000,icmp6,icmp_type=152,action=drop
# Multicast router termination.
in_port={port},priority=6000,icmp6,icmp_type=153,action=drop
# Fsck all the rest
in_port={port},priority=100,action=drop
'''

CLEANUPFLOWS_CMD = '''\
ovs-ofctl del-flows {bridge} "in_port={port}";
ovs-ofctl del-flows {bridge} "dl_src={mac}";
ovs-ofctl del-flows {bridge} "dl_dst={mac}";
'''

GWMGMTINPUT = '''\
# drop network chatter
table=0,priority=100,dl_src=01:00:00:00:00:00/01:00:00:00:00:00, actions=drop
# drop all UDP
table=0,priority=100,dl_type=0x0800,nw_proto=17,actions=drop
# drop all ipv6
table=0,in_port={port},priority=100,dl_src={mac},dl_type=0x86dd,actions=drop
# send rest in table 1
table=0, priority=0, actions=resubmit(,1)
# Table 1 ; stateful packet filter ( ovs >= 2.5 )
# start dropping it all (fallthrough (lowest priority))
table=1,priority=1,action=drop
# allow all arp (for now)
table=1,priority=10,arp,nw_src={ipaddress},action=normal
table=1,priority=10,arp,nw_dst={ipaddress},action=normal
# when an ip packet arrives and is not tracked, send it to the conntracker and continue table2
table=1,priority=100,ip,ct_state=-trk,action=ct(table=2)
# a packet from 10... with dest MAC, that is IP, and is a NEW session packet, commit it in conntracker
table=2,nw_src=10.199.0.0/22,dl_dst={mac},ip,ct_state=+trk+new,action=ct(commit),normal
# and do normal packet forwarding processing on it
table=2,nw_src=10.199.0.0/22,dl_dst={mac},ip,ct_state=+trk+est,action=normal
# otherwise, all new IP sessions get dropped
table=2,in_port={port},ip,ct_state=+trk+new,action=drop
# unless they are related to a comitted session
table=2,in_port={port},ip,ct_state=+trk+est,action=normal
# fall through over prio 10 and 1 (specified above)
'''
