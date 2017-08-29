# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#


/interface pptp-server
remove [/interface pptp-server find name=pptp-in1]
add name=pptp-in1 user=admin

/ppp profile
set 0 bridge=cloudspace-bridge local-address=192.168.103.1 \
    remote-address=dhcpppp use-encryption=required

/interface ovpn-server server
set certificate="server.crt_0" cipher=blowfish128,aes128,aes192,aes256 enabled=yes \
    keepalive-timeout=disabled mode=ethernet

/interface pptp-server server
set enabled=yes authentication=pap,chap,mschap1,mschap2 mrru=1600

/ppp
secret remove numbers=[/ppp secret find]
/ppp secret add name=vpn service=any password="$vpnpassword"
