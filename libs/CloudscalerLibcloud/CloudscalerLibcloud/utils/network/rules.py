PUBLICINPUT = '''\
# Allow dhcp client
in_port={port},priority=8000,udp,tp_dst=67,dl_src={mac},idle_timeout=0,action=normal
# Allow arp request/replies only specifically from that ip/mac combo
in_port={port},priority=7000,arp,arp_op=2,dl_src={mac},nw_src={publicipv4addr}/32,action=normal
in_port={port},priority=7000,arp,arp_op=1,dl_src={mac},nw_src={publicipv4addr}/32,action=normal
# Drop DHCP server replies coming from here (rogue dhcp server)
in_port={port},priority=8000,udp,tp_src=68,dl_src={mac},idle_timeout=0,action=drop
# Allow ipv4/mac (note: this is a /32). "There can be only one!" (sic McLeod)
in_port={port},priority=6000,ip,dl_src={mac},nw_src={publicipv4addr}/32,idle_timeout=0,action=normal
# Fsck all the rest (that means also no IPV6)
in_port={port},priority=100,action=drop
# but for everything coming back, (or in, for that matter), allow
priority=0,actions=normal
'''

CLEANUPFLOWS_CMD = '''\
ovs-ofctl del-flows {bridge} "in_port={port}";
ovs-ofctl del-flows {bridge} "dl_src={mac}";
ovs-ofctl del-flows {bridge} "dl_dst={mac}";
'''

CLEANUPFLOWS_CMD_IP = '''\
ovs-ofctl del-flows {bridge} "ip,nw_src={ipaddress}";
ovs-ofctl del-flows {bridge} "ip,nw_dst={ipaddress}";
ovs-ofctl del-flows {bridge} "arp,nw_src={ipaddress}";
'''

GWMGMTINPUT = '''\
# drop network chatter
table=0, priority=100,dl_src=01:00:00:00:00:00/01:00:00:00:00:00, actions=drop
#allow arp
table=0, priority=100,arp actions=normal
# drop all ipv6
table=0, priority=100,ipv6,actions=drop
# if mac/ip combo fit, continue into t1
# table=0, priority=10,ip,nw_src={ipaddress}/32,dl_src={mac} actions=resubmit(,1)
# table=0, priority=10,ip,nw_dst={ipaddress}/32,dl_dst={mac} actions=resubmit(,1)
table=0, priority=10,tcp, actions=resubmit(,1)
table=0, priority=1,actions=drop

#first, if udp -> binary heaven
table=1, priority=100,udp actions=drop
# if untracked, send into conntrack and follow t2
table=1, ct_state=-trk,ip actions=ct(table=2)
# if already tracked : t2
table=1, ct_state=+trk,ip actions=resubmit(,2)

# going to ros, commit as flow -> t3
table=2, priority=200,ct_state=+trk,ip,dl_dst={mac} actions=ct(commit,table=3)
#  coming from ros as new , drop
table=2, priority=200,ct_state=+new+trk,ip,dl_src={mac} actions=drop
# normal send to os for routing
table=2, priority=100 actions=NORMAL

# commited flow, but now from ROS -> drop
table=3, priority=300,ct_state=+new+trk,ip,dl_src={mac} actions=drop
# rest same as t2
table=3, priority=200,ct_state=+new+trk,ip,dl_dst={mac}, actions=normal
table=3, priority=200,ct_state=+est+trk,ip actions=normal

'''
