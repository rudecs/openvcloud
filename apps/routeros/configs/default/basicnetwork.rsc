# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#


/interface bridge
remove [/interface bridge find name=cloudspace-bridge]
add name=cloudspace-bridge arp=proxy-arp

/interface ethernet
set [ find default-name=ether2 ] arp=proxy-arp name=cloudspace
set [ find default-name=ether3 ] name=internal
set [ find default-name=ether1 ] name=public

/interface bridge port
remove [/interface bridge port find name=cloudspace]
add bridge=cloudspace-bridge interface=cloudspace

/ip pool
remove [/ip pool find name=dhcp]
# add name=dhcp ranges=192.168.103.11-192.168.103.254
add name=dhcpppp ranges=192.168.103.2-192.168.103.10

/ip dns set allow-remote-requests=no

/ip dhcp-server network
remove [/ip dhcp-server network find]
add address=192.168.103.0/24 gateway=192.168.103.1 netmask=255.255.255.0 dns-server=8.8.8.8

/ip dhcp-server
remove [/ip dhcp-server find name=server1]
add disabled=no interface=cloudspace-bridge name=server1 lease-time=5200w
config set store-leases-disk=immediately

/ip dhcp-client
remove [find]

/ip address
remove numbers=[/ip address find interface=public]
remove numbers=[/ip address find interface=cloudspace-bridge]
add interface=public address=$pubip
add interface=cloudspace-bridge address=$privateip

/ip neighbor
discovery set [ /interface ethernet find name=public ] discover=no

/interface ethernet reset-mac-address numbers=0
/interface ethernet reset-mac-address numbers=1
/interface ethernet reset-mac-address numbers=2

/ip firewall nat
add action=masquerade chain=srcnat out-interface=public

