#!/bin/bash

environment=$1
node=$2
ctrlport=$3
repodir="/opt/code/github/gig-projects/"
userrepodir="$HOME/code/github/gig-projects/"
if [ -e $userrepodir ]; then
    repodir=$userrepodir
fi
if ! mkdir -p $repodir; then
    echo "No write permission on $repodir using $userrepodir instead"
    repodir="$userrepodir"
    if ! mkdir -p $repodir; then
        echo "Make sure you have permission on $repodir"
        exit 1
    fi
fi
envrepo="${repodir}/env_${environment}"
if [ ! -e ${envrepo} ]; then
    pushd $repodir > /dev/null
    git clone git@github.com:gig-projects/env_$environment
    popd > /dev/null
fi

function checknode() {
    nodeservice="${envrepo}/services/jumpscale__node.ssh__${node}/service.hrd"
    nnodeservice="${envrepo}/services/jumpscale__node.ssh__ovc_${node}/service.hrd"
    if [ -e ${nodeservice} ]; then
        return 0
    elif [ -e ${nnodeservice} ]; then
        nodeservice=$nnodeservice
        node="ovc_$node"
        return 0
    elif [ -n "${nodeid}" ]; then
        nodeservice="${envrepo}/services/jumpscale__node.ssh__cpu-${nodeid}.${environment}/service.hrd"
        if [ -e ${nodeservce} ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}


if [ "$node" != git ]; then
    if ! checknode; then
        pushd $envrepo > /dev/null
        git pull
        popd > /dev/null
    fi
    if ! checknode; then
        echo "Could not find node $node"
        exit 1
    fi
fi
sshkey="${envrepo}/keys/git_root"
chmod 600 $sshkey
# if [ -e "${envrepo}/services/jumpscale__node.ssh__ovc_reflector" ]; then
#     host="${environment}.demo.greenitglobe.com"
#     port=22
# else
#     masterservice="${envrepo}/services/jumpscale__node.ssh__ovc_master/service.hrd"
#     host=$(grep 'publicip' $masterservice | egrep -o "[0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
#     port=$(grep 'publicport' $masterservice | egrep -o "[0-9]+{2,5}")
# fi
host="${environment}.demo.greenitglobe.com"
port=22
args=""


function hostip() {
    ssloffloader_service="${envrepo}/services/jumpscale__node.ssh__ovc_proxy/openvcloud__ssloffloader__main/service.hrd"
    egrep "instance\.master\.ipadress" $ssloffloader_service | egrep -o "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
}

function fwdport() {
    grep "instance.ssh.port" "${nodeservice}" | egrep -o "[0-9]{2,5}"
}

case $node in
    git)
        port=22
        ;;
    *)
        fwdport="$(fwdport)"
        proxy="\"ssh -A -M -l root -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $sshkey -q $host -p $ctrlport nc -q0 %h $fwdport\""
        host="$(hostip)"
esac

result="SSHKEY=$sshkey; PROXY=$proxy; HOST=$host"
echo $result
