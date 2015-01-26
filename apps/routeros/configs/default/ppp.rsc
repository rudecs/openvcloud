# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#


/interface pptp-server 
remove [/interface pptp-server find name=pptp-in1]
add name=pptp-in1 user=admin

/ip pool
remove [/ip pool find name=dhcpppp]
add name=dhcpppp ranges=192.168.103.240-192.168.103.244

/ip dhcp-server
remove [/ip dhcp-server find name=server1]
add address-pool=dhcp disabled=no interface=cloudspace-bridge name=server1

/ppp profile
set 0 bridge=cloudspace-bridge local-address=192.168.103.1 remote-address=\
    dhcpppp use-encryption=required

/interface ovpn-server server
set certificate=cert_1 cipher=blowfish128,aes128,aes192,aes256 enabled=yes \
    keepalive-timeout=disabled mode=ethernet

/interface pptp-server server
set enabled=yes authentication=pap,chap,mschap1,mschap2 mrru=1600
