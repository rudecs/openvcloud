function ipnse(){ ns=$1 ; shift ; ip netns exec ns-${ns} $@ ;}
function ipla(){ ip link add $@ ;}
function no6(){ sysctl -w net.ipv6.conf.${1}.disable_ipv6=1 ;}



for i in `seq 1 50` ; do 
    num=`printf "%04d" $i`
    ipla pubtons-${num} type veth peer name pubinns-${num}
    no6 pubtons-${num}
    ovs-vsctl add-port BR-${num} pubtons-${num}
    ip l set pubtons-${num} up
    ip netns add ns-${num}
    ip link set pubinns-${num} netns ns-${num}
    ipnse ${num} ip link set lo up
    ipnse ${num} ip link set pubinns-${num} mtu 1450 multicast on
    ipnse ${num} ip link set pubinns-${num} up
    ipnse ${num} ip addr add 192.168.1.1/24 dev pubinns-${num}
done

