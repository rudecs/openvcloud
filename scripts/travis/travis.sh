#!/bin/bash

execute(){
    sshpass -p ${password} ssh -o StrictHostKeyChecking=no -t ${username}@${ipaddress} ${1}
}

echo "[+] Joining zerotier network ${zerotier_network} ..."
sudo zerotier-cli join ${zerotier_network}; sleep 5
memberid=$(sudo zerotier-cli info | awk '{print $3}')
curl -s -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotier_token}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotier_network}/member/${memberid} > /dev/null
sudo ifconfig "$(ls /sys/class/net | grep zt)" mtu 1280 

for i in {1..20}; do
    ping -c1 ${ipaddress} > /dev/null && break
done

if [ $? -gt 0 ]; then
    echo "Can't reach ip address ${ipaddress}"; exit 1
fi

echo "Running tests ..."
execute "cd /opt/code/github/0-complexity/openvcloud/tests; bash run_tests.sh -t ${1} -p ${2}"
