#!/bin/bash

function execute() {
    sshpass -p ${password} ssh -o StrictHostKeyChecking=no -t ${username}@${ipaddress} ${1}
}

function join_zerotier() {
    sudo zerotier-cli join ${ZEROTIER_NETWORK}; sleep 5
    memberid=$(sudo zerotier-cli info | awk '{print $3}')
    curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${ZEROTIER_TOKEN}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${ZEROTIER_NETWORK}/member/${memberid} > /dev/null
    sudo ifconfig "$(ls /sys/class/net | grep zt)" mtu 1280 
    for i in {1..20}; do
        ping -c1 ${ipaddress} > /dev/null && break
    done
    if [ $? -gt 0 ]; then
        echo "Can't reach ip address ${ipaddress}"; exit 1
    fi
}

function run_tests() {
    echo "Joining zerotier network ${ZEROTIER_NETWORK} ..."
    join_zerotier 

    echo "Running tests ..."
    execute "cd /opt/code/github/0-complexity/openvcloud/tests; bash run_tests.sh ${1} ${2}"
}

function push_results() {
    TESTSUITE=${1}
    TIMESTAMP=$(date "+%m-%d-%y")
    LOGFILE="/tmp/${TESTSUITE}.log"
    REMOTE_LOGFILE="/${TIMESTAMP}/${TRAVIS_BUILD_NUMBER}/${TESTSUITE}.log"
    
    echo "Uploading results ..."
    execute "s3cmd --access_key ${S3_KEY} --secret_key ${S3_SECRET} --host ${S3_HOST} --host-bucket ${S3_HOST} --no-ssl put ${LOGFILE} s3://${S3_LOGS_BUCKET}/${REMOTE_LOGFILE}"
}

while true; do
  case "$1" in
    --run-test) run_tests ${2} ${3}; shift ;;
    --push-result) push_results ${2}; shift ;;
    * ) break ;;
  esac
  shift
done
