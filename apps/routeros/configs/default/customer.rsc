# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#
/user
remove [/user find name=admin]
remove [/user find name=customer]

/user group
remove [/user group find name=customer]
add name=customer policy="local,reboot,read,write,policy,web,telnet,!ssh,!ftp,!test,!winbox,!password,!sniff,!sensitive,!api"

/user
add name=admin password="$password" group=customer

