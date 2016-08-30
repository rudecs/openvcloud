# OVS node failure recovery steps

Today the OVS edge client is not HA yet, meaning that when an OVS volumedriver node crashes, it does not fail over to another volumedriver node in the storage cluster.

To be able to recover from this we need to
- remove the node from the OVC model to prevent that new vms take this volumedriver node
- bring al the vms down that have storage disks on this OVS volumedriver node
- remove the node from the storage cluster via OVS interface
- reassign the vdisks of the affected vms over the remaining OVS volumedriver nodes
- bring up al the vms that we brought down in step 2

**Remark**: I could be that there are vms that are stopped in step 2. We MUST NOT bring them up in step 5

## teardown script [step 2]

Scriptname: ovs_storage_tear_down_vms.py
Arguments:
- ipaddress of the storage node that has failed
- filename in which it will save the vms that were brought down

## restart script [step 4 & 5]

Scriptname: ovs_storage_bring_up_vms.py
Arguments:
- ipaddress of the storage node that has failed
- filename from which it will load the vms that were brought down, which need to be started again.
