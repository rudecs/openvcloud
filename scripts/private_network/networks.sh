for i in `seq 1 50` ; do 
    num=`printf "%04d" $i`
    tag=$(($i+200))
    ovs-vsctl --if-exists del-port BR-${num} trp-${num}
    ovs-vsctl --if-exists del-port BR-${num} ipp-${num}
    ovs-vsctl --if-exists del-port vxbackend brp-${num}
    ovs-vsctl --if-exists del-br BR-${num}
    virsh net-destroy default_${i}
    virsh net-undefine default_${i}
done

for i in `seq 1 50` ; do 
    num=`printf "%04d" $i`
    tag=$(($i+200))
    ovs-vsctl add-br BR-${num}
    ovs-vsctl add-port vxbackend brp-${num} tag=${tag} -- set Interface brp-${num} type=patch options:peer=trp-${num}
    ovs-vsctl add-port BR-${num}   trp-${num}          -- set Interface trp-${num} type=patch options:peer=brp-${num}
# test interface, not needed
    ovs-vsctl add-port BR-${num}   ipp-${num}          -- set Interface ipp-${num} type=internal
    cat << EOF > net.xml
<network>
<name>default_$(echo $i)</name>
<forward mode="bridge"/>
<bridge name='BR-${num}'/>
<virtualport type='openvswitch'/>
</network>
EOF
    virsh net-define net.xml
    virsh net-start default_${i}
    virsh net-autostart default_${i}
done
