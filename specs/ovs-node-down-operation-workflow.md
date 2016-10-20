# OVS node failure recovery steps

Today the OVS edge client is not HA yet, meaning that when an OVS volumedriver node crashes, it does not fail over to another volumedriver node in the storage cluster.

To be able to recover from this we need to
- remove the node from the OVC model to prevent that new vms take this volumedriver node
- remove the node from the storage cluster via OVS interface
- bring al the vms down that have storage disks on this OVS volumedriver node
- reassign the vdisks of the affected vms over the remaining OVS volumedriver nodes
- bring up al the vms that we brought down in step 3

**Remark**: I could be that there are vms that are stopped in step 3. We MUST NOT bring them up in step 5

## ovs_stroragedriver_outage script [step 3, 4 & 5]

Scriptname: ovs_stroragedriver_outage.py
Arguments:
- ipaddress of the storage node that has failed

