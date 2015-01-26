# mar/17/2014 20:32:30 by RouterOS 6.10
# software id = 4I7C-Y1J9
#
/certificate
add common-name=codescalers.com country=EG locality=NC name=cert_1 \
    organization=codescalers.com state=CA subject-alt-name=\
    email:mahmoud@codescalers.com trusted=yes unit=codescalers.com
add common-name=vscalers.com country=BE locality=BR name=cert_2 organization=\
    vscalers.com state=CA subject-alt-name=email:info@vscalers.com trusted=\
    yes unit=vscalers.com

/interface bridge
add name=cloudspace-bridge
/interface ethernet
set [ find default-name=ether2 ] arp=proxy-arp name=cloudspace
set [ find default-name=ether3 ] name=internal
set [ find default-name=ether1 ] name=public

/interface pptp-server
add name=pptp-in1 user=admin
/ip hotspot user profile
set [ find default=yes ] idle-timeout=none keepalive-timeout=2m \
    mac-cookie-timeout=3d
/ip pool
add name=dhcp ranges=192.168.1.3-192.168.1.254
add name=dhcpppp ranges=192.168.1.240-192.168.1.244
/ip dhcp-server
add address-pool=dhcp disabled=no interface=cloudspace-bridge name=server1
/port
set 0 name=serial0
/ppp profile
set 0 bridge=cloudspace-bridge local-address=192.168.1.1 remote-address=\
    dhcpppp use-encryption=required


/user group
add name=customer policy="local,reboot,read,write,policy,web,!telnet,!ssh,!ftp\
    ,!test,!winbox,!password,!sniff,!sensitive,!api"

/interface bridge port
add bridge=cloudspace-bridge interface=cloudspace


/interface ovpn-server server
set certificate=cert_1 cipher=blowfish128,aes128,aes192,aes256 enabled=yes \
    keepalive-timeout=disabled mode=ethernet
/interface pptp-server server
set authentication=pap,chap,mschap1,mschap2 mrru=1600

/ip address
add address=10.199.3.254/22 interface=internal network=10.199.0.0
add address=192.168.1.1/24 interface=cloudspace-bridge network=192.168.1.0
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=8.8.8.8 gateway=192.168.1.1
/ip dns
set allow-remote-requests=yes
/ip dns static
add address=192.168.88.1 name=router

/ip firewall nat
add action=masquerade chain=srcnat out-interface=public to-addresses=0.0.0.0

/ip route
add comment="added by setup" distance=1 gateway=192.198.94.1

/ip upnp
set allow-disable-external-interface=no
/system identity
set name=Vscalers

/system script
add name=reset_mac policy=reboot source=reset_mac
