#!/bin/bash
set -e
environment=""
branch=""
noconnect=""
while getopts ":e:b:hn" opt; do
  case $opt in
    e)
      environment="$OPTARG"
      ;;
    b)
      branch="$OPTARG"
      ;;
    n)
      noconnect="true"
      ;;
    h)
      echo "Usage pre-install.sh [options] url:
      -e pass environment name
      -b pass branch name (only master supported)
      -n do not create reverse ssh tunnel (autossh)
      "
      exit 44
  esac
done
shift $((OPTIND-1))
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

if [ "$branch" != "master" ]; then
	if [ ! -f /tmp/branch.sh ]; then
		echo "[-] /tmp/branch.sh not found"
		exit 1
	fi

	source /tmp/branch.sh

	if [ "$JSBRANCH" == "" ]; then
		echo "[-] no branch set"
		exit 1
	fi

	echo "[+] jumpscale branch: $JSBRANCH"
	echo "[+] ays repo branch: $AYSBRANCH"
	echo "[+] openvcloud branch: $OVCBRANCH"
else
	echo "[+] installing from master"
fi

BOOTSTRAP="http://${1}:5000"

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
	curl https://raw.githubusercontent.com/Jumpscale7/jumpscale_core7/master/install/install.sh > /tmp/js7.sh
	JSBRANCH=$JSBRANCH AYSBRANCH=$AYSBRANCH bash /tmp/js7.sh
else
	echo "[+] jumpscale already installed"
fi

if ! grep openvcloud_ays /opt/jumpscale7/hrd/system/atyourservice.hrd > /dev/null; then
	echo "[+] configuring atyourservice"
	echo "metadata.openvcloud            =" >> /opt/jumpscale7/hrd/system/atyourservice.hrd
	echo "    branch:'$OVCBRANCH'," >> /opt/jumpscale7/hrd/system/atyourservice.hrd
	echo "    url:'git@github.com:0-complexity/openvcloud_ays'," >> /opt/jumpscale7/hrd/system/atyourservice.hrd
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
HOST=$(hostname -s)

if [ "$2" != "--no-connect" ]; then
	echo "[+] bootstrapping node id: $NODE"
	ays install -n bootstrap_node --data "instance.bootstrapp.addr=${BOOTSTRAP}#"
fi

echo "[+] ready, have a nice day."
