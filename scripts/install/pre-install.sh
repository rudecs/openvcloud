#!/bin/bash
if [ "$1" == "" ]; then
	echo "Usage: pre-install.sh remote-host"
	exit 1
fi

if [ "$SSH_AUTH_SOCK" == "" ]; then
	echo "[-] no ssh authentification found, checking anyway"
	
	AGENT=$(ssh-add -L > /dev/null 2>&1)
	
	if [ $? != 0 ]; then
		echo "[-] no ssh key found or agent is not running."
		exit 1
		
	else
		echo "[-] ssh agent seems okay"
	fi
fi

# print loaded keys
ssh-add -L | awk '{ print "[+] ssh agent key found: " $3 }'

if [ "${x::4}" == "http" ]; then
	echo "[-] remote host should be a hostname, not an url"
	exit 1
fi

REMOTEADDR="$1"

# REMOTEADDR=37.203.43.120   # du-conv-2
# REMOTEADDR=37.203.43.127   # du-conv-1
# REMOTEADDR=185.69.164.155  # be-conv-2
# REMOTEADDR=37.203.43.122   # be-dev-1
# REMOTEADDR=185.69.164.158  # be-stor-1

BOOTSTRAP="http://${REMOTEADDR}:5000"

LASTTIME=$(stat /var/lib/apt/periodic/update-success-stamp | grep Modify | cut -b 9-)
LASTUNIX=$(date --date "$LASTTIME" +%s)
echo "[+] last apt-get update: $LASTTIME"

if [ $LASTUNIX -gt $(($(date +%s) - (3600 * 6))) ]; then
	echo "[+] skipping system update"
else
	echo "[+] updating system"
	apt-get update
fi

if [ ! -d /opt/jumpscale7 ]; then
	echo "[+] installing Jumpscale"
	curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh
else
	echo "[+] jumpscale already installed"
fi

TEST=$(grep openvcloud_ays /opt/jumpscale7/hrd/system/atyourservice.hrd)
if [ $? == 1 ]; then
	echo "[+] configuring atyourservice"
	echo "metadata.openvcloud            =" >> /opt/jumpscale7/hrd/system/atyourservice.hrd
	echo "    url:'https://git.aydo.com/0-complexity/openvcloud_ays'," >> /opt/jumpscale7/hrd/system/atyourservice.hrd
else
	echo "[+] atyourservice already configured"
fi

echo "[+] setting up username/password"
jsconfig hrdset -n whoami.git.login -v "ssh"
jsconfig hrdset -n whoami.git.passwd -v "ssh"

echo "Host git.aydo.com" >> /root/.ssh/config
echo "    StrictHostKeyChecking no" >> /root/.ssh/config
echo "" >> /root/.ssh/config

echo "Host github.com" >> /root/.ssh/config
echo "    StrictHostKeyChecking no" >> /root/.ssh/config
echo "" >> /root/.ssh/config

echo "[+] loading settings"
HOST=$(hostname)

# Note: need to be prefixed by 10# otherwise
# evaluation will fail on 8 and 9 (octal value)
NODE=$((10#$(echo ${HOST##*-})))

if [ "$NODE" == "" ]; then
	echo "[-] cannot detect node id"
	exit
fi

echo "[+] bootstrapping node id: $NODE"
ays install -n bootstrap_node --data "instance.bootstrapp.addr=${BOOTSTRAP}#instance.node.id=${NODE}#"

echo "[+] ready, have a nice day."
