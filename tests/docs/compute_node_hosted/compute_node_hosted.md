## Functional Tests Hosted on a Compute Node

Three types of automated functional tests are available for OpenvCloud:
- Tests that run on **ovc_master**, discussed [elsewhere in this guide](../ovc_master_hosted/ovc_master_hosted.md)
- Tests that run on a physical **compute node**, discussed here below
- Tests that can run on any **remote machine**, discussed [elsewhere in this guide](../remote_machine_hosted/remote_machine_hosted.md)

The differences with these tests is that they have been designed to run on a physical compute node.

Following functional tests require access to the physical compute nodes:

* [Network Configuration Test](1_network_config_test/1_network_config_test.md)
* [Virtual Machines Limit Test](3_Env_Limit_test/3_Env_Limit_test.md)
* [Cloud Spaces Limit Test](5_cloudspace_limits_test/5_cloudspace_limits_test.md)
* [VM Live Migration Test](6_vm_live_migration_test/6_vm_live_migration_test.md)
* [Node Maintenance Test](8_node_maintenance_test/8_node_maintenance_test.md)
* [Snapshots Limit Test](9_vm_unlimited_snapshots/9_vm_unlimited_snapshots.md)

How to get access to a physical compute node is documented in the [OpenvCloud Operator's Guide](https://www.gitbook.com/book/gig/ovcdoc_public/details), see the [Connect to an Environement](https://gig.gitbooks.io/ovcdoc_public/content/Sysadmin/Connect/connect.html) section for all details.
