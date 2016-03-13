#!/bin/bash

# this script should be run on a fresh ubuntu 14.10
# it install jumpscale and clone openvcloud repositories
# to allow initiate an openvcloud setup

JSBRANCH="7.0"
AYSBRANCH="7.0"
OVCBRANCH="2.0"

echo "[+] updating system"
apt-get -q update

# checking for ssh-agent
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

echo "[+] installing essentials"
apt-get -y install vim

if [ ! -d /opt/jumpscale7 ]; then
	echo "[+] installing Jumpscale ($JSBRANCH, $AYSBRANCH)"
	curl https://raw.githubusercontent.com/Jumpscale7/jumpscale_core7/master/install/install.sh > /tmp/js7.sh
	JSBRANCH=$JSBRANCH AYSBRANCH=$AYSBRANCH bash /tmp/js7.sh
else
	echo "[+] jumpscale already installed"
fi

if ! grep "Host git.aydo.com" /root/.ssh/config > /dev/null 2>&1; then
	echo "[+] patching ssh for git.aydo.com"
	echo "Host git.aydo.com" >> /root/.ssh/config
	echo "    StrictHostKeyChecking no" >> /root/.ssh/config
	echo "" >> /root/.ssh/config
else
	echo "[+] git.aydo.com already patched"
fi

if ! grep "Host github.com" /root/.ssh/config > /dev/null 2>&1; then
	echo "[+] patching ssh for github.com"
	echo "Host github.com" >> /root/.ssh/config
	echo "    StrictHostKeyChecking no" >> /root/.ssh/config
	echo "" >> /root/.ssh/config
else
	echo "[+] github.com already patched"
fi

if ! grep openvcloud_ays /opt/jumpscale7/hrd/system/atyourservice.hrd > /dev/null 2>&1; then
	echo "[+] configuring atyourservice"
	echo "metadata.openvcloud            =" >> /opt/jumpscale7/hrd/system/atyourservice.hrd
	echo "    branch:'${OVCBRANCH}'," >> /opt/jumpscale7/hrd/system/atyourservice.hrd
	echo "    url:'git@github.com:0-complexity/openvcloud_ays'," >> /opt/jumpscale7/hrd/system/atyourservice.hrd
else
	echo "[+] atyourservice already configured"
fi

echo "[+] setting up username/password"
jsconfig hrdset -n whoami.git.login -v "ssh"
jsconfig hrdset -n whoami.git.passwd -v "ssh"
git config --global user.email "maxime@incubaid.com"
git config --global user.name "Maxime Daniel"

echo "[+] updating openvcloud"
ays mdupdate
ays install -n portal_lib
ays install -n redis -i system --data 'param.disk:1 param.ip:0.0.0.0 param.mem:100 param.passwd: param.port:9999 param.unixsocket:0 '

echo "[+] installing 0-complexity/openvcloud"
ays install -n libcloudlibvirt

apt-get install -y python-pip
pip install gitlab3

echo "[+] openvcloud configured"
