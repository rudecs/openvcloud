#!/bin/bash
USERNAME=danielma
PASSWORD=gitlabpasswd

if [ "$1" == "" ]; then
	echo "Usage: pre-install.sh remote-host"
	exit 1
fi

if [ "${x::4}" == "http" ]; then
	echo "[-] remote host should be a hostname, not an url"
	exit 1
fi

REMOTEADDR="$1"
BOOTSTRAP="http://${REMOTEADDR}:5000"

echo "[+] updating"
apt-get update

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
# FIXME
jsconfig hrdset -n whoami.git.login -v "$USERNAME"
jsconfig hrdset -n whoami.git.passwd -v "$PASSWORD"

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
