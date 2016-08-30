## Open vStorage Configuration

The actual installation of Open vStorage is done as part of the installation of the the OpenvCloud nodes.

Here we discuss the configuration of Open vStorage, which you will need to do manually (for now) through the WebUI of Open vStorage.


### Set roles to SSD disks

In each storage router you will need to assign the DB, Write, Read and Scrub roles.

In order to do so goto `Storages Routers -> Disks`, and use following configuration for each node:
- `/mnt/cache1` as `DB, Write` roles
- `/mnt/cache2` as `Read` role
- `/var/tmp` as `Scrub` role


### Create the Backend

Backends
- Add Backend
- Name: use environment name
- Initialize all Disks
- Claim all Disks


### Add the OpenvCloud Preset

From the ovc_git machine, please run:

```bash
cd /opt/code/git/openvcloudEnvironments/be-dev-1/
jspython scripts/ovs-setup.py
```


### Create the vPool

vPools
- Add new vPool
- Name: `vmstor`
- Type: `Open vStorage Backend`
- Backend: the one created previously
- Preset: `alba-openvcloud`

- Read Cache: put `80%` of the size in the box
- SCO Size: `64 MiB`
- Write Buffer: `1024 MiB`


When created:
- Management actions:
- Add all nodes


### Finish

Open vStorage should be ready!