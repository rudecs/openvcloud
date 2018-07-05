## Functional Tests Hosted on ovc_master

Three types of automated functional tests are available for OpenvCloud:
- Tests that run on **ovc_master**, discussed here below
- Tests that run on a physical **compute node**, discussed [elsewhere in this guide](../compute_node_hosted/compute_node_hosted.md)
- Tests that can run on any **remote machine**, discussed [elsewhere in this guide](../remote_machine_hosted/remote_machine_hosted.md)

> Remember: **ovc_master** is the virtual machine in the master cloud space where the **Cloud Broker Portal** is running, and all other OpenvCloud portals

Currently only the API test suites are designed to be installed (hosted) on and run from **ovc_master**.

There are two API tests suites for the OpenvCloud API:
- Access Control List API
- OpenvCloud API (covering all non-ACL APIs)

Both are discussed [here](API/API.md).
