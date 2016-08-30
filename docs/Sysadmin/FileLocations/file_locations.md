## File Locations


### Introduction

All important files are located in the directory `/opt`.

Under `/opt` there are at least two sub directories:
- `/opt/jumpscale7`- containing all files related to the JumpScale platform and the locally installed applications
- `/opt/code` - containing all Git repositories that have been cloned on the machine

Under `opt/code/` there are always two sub directories:
  - `/opt/code/github` containing all cloned repositories hosted at GitHub
  - `/opt/code/git` containing all other cloned repositories, such as those hosted at https://git.aydo.com/ ("AYDO")

Under `opt/code/git/`:
```
0-complexity
binary
```

Under `opt/code/git/0-complexity`:
```
openvcloud
openvcloud_ays
```

Under `opt/code/github`:
```
ays_jumpscale7
jumpscale_core7
jumpscale_portal
```

Depending on the role of the machine more directories and sub directories exist.

In what follows we will provide more details for each of the below roles:

- Physical node
- ovc_git
- ovc_master
- ovc_reflector
- ovc_dcpm
- ovc_proxy


### Files on physical node

On a physical node, under `/opt/code/github` next to `/opt/code/github/jumpscale` you will also find `/opt/code/github/0-complexity`, only including the subdirectory `novnc`, a cloned repository from https://github.com/0-complexity/noVNC - used for the console in the User Portal.

Next to `/opt/jumpscale7` and `/opt/code` following sub directories exist under `/opt/`:
- alba-asmanager
- build
- nginx
- openvstorage
- OpenvStorage
- statsd-collector

Under `/opt/jumpscale7` there is the sub directory `/opt/jumpscale7/hrd/apps` containing all configuration files of the locally installed applications:

```
root@be-scale-1-05:/opt/jumpscale7/hrd/apps# ls -1
jumpscale__agentcontroller_client__main
jumpscale__autossh__be-scale-1-01
jumpscale__autossh__http_proxy
jumpscale__base__main
jumpscale__jsagent__main
jumpscale__nginx__main
jumpscale__nodejs__main
jumpscale__osis_client__jsagent
jumpscale__osis_client__main
jumpscale__portal_client__cbportal
jumpscale__portal_client__cloudbroker
jumpscale__portal_client__main
jumpscale__portal_lib__main
jumpscale__python_portal__main
jumpscale__redis__system
jumpscale__statsd-collector__main
openvcloud__bootstrap_node__main
openvcloud__cb_cpunode_aio__main
openvcloud__compute_kvm_base__main
openvcloud__compute_node__main
openvcloud__image_ubuntu-1404-x64__main
openvcloud__libcloudlibvirt__main
openvcloud__openvstorage__main
openvcloud__openwrt-remote-manager__main
openvcloud__ovs_alba_oauthclient__main
openvcloud__ovs_branding__main
openvcloud__scaleout_networkconfig__main
openvcloud__vfwnode__main
openvcloud__vncproxy__main
```

> Never configure these applications locally, everything gets pushed from ovc_git.

On a physical node you will also find the virtual machines images which are available on that node, this under `/mnt/vmstor/templates/`:
```
root@be-scale-1-01:/mnt/vmstor/templates# ls -1
createtemplate_1452100540.37.raw
Ubuntu.1404.uefi.x64.raw
```

### Files on ovc_git

ovc_git is one of the virtual machines in the master cloud Space, its role is limited to central Git repository, from which all physical nodes clone.

Under `/opt/code/git/openvcloudEnvironments` there is a sub directory per environment managed by the master cloud space to which ovc_git belongs. In a typically setup a master cloud space will only manage one environment, so only one sub directory will exist under `/opt/code/git/openvcloudEnvironments`, having the name of the environment, i.e, `be-scale-1`.

Under this environment directory, follows sub directories exist:
- **Mikrotik** holding some configuration information of management gateway/router
- **keys** holding SSH private and public keys of the virtual machines in the master cloud space
- **scripts** containing installation scripts
- **services** containing the AYS recipes of all remote (to ovc_git) services running in the environment - discussed below
- **service templates** - always empty

The most important information is the `services` directory:

```
root@ovcgit:/opt/code/git/openvcloudEnvironments/be-scale-1/services# ls -1
jumpscale__autossh__be-scale-1-01
jumpscale__autossh__be-scale-1-02
jumpscale__autossh__be-scale-1-03
jumpscale__autossh__be-scale-1-04
jumpscale__autossh__be-scale-1-05
jumpscale__autossh__be-scale-1-06
jumpscale__autossh__be-scale-1-07
jumpscale__autossh__be-scale-1-08
jumpscale__autossh__be-scale-1-09
jumpscale__autossh__be-scale-1-10
jumpscale__ms1_client__main
jumpscale__node.ssh__be-scale-1-01
jumpscale__node.ssh__be-scale-1-02
jumpscale__node.ssh__be-scale-1-03
jumpscale__node.ssh__be-scale-1-04
jumpscale__node.ssh__be-scale-1-05
jumpscale__node.ssh__be-scale-1-06
jumpscale__node.ssh__be-scale-1-07
jumpscale__node.ssh__be-scale-1-08
jumpscale__node.ssh__be-scale-1-09
jumpscale__node.ssh__be-scale-1-10
jumpscale__node.ssh__ovc_dcpm
jumpscale__node.ssh__ovc_master
jumpscale__node.ssh__ovc_proxy
jumpscale__node.ssh__ovc_reflector
jumpscale__portal_lib__main
jumpscale__sshkey__nodes
jumpscale__sshkey__ovc_dcpm
jumpscale__sshkey__ovc_master
jumpscale__sshkey__ovc_proxy
jumpscale__sshkey__ovc_reflector
openvcloud__bootstrapp__main
openvcloud__git_vm__main
openvcloud__ovc_cs_aio__main
openvcloud__ovc_namer__main
openvcloud__ovc_setup__main
openvcloud__ovs_setup__main
```

Here you then find sub directories for with the AYS recipes of the child services of each of the parents listed, i.e. for `jumpscale__node.ssh__be-scale-1-04`:
```
root@ovcgit:/opt/code/git/openvcloudEnvironments/be-scale-1/services# cd jumpscale__node.ssh__be-scale-1-04
root@ovcgit:/opt/code/git/openvcloudEnvironments/be-scale-1/services/jumpscale__node.ssh__be-scale-1-04# ls -1
jumpscale__agentcontroller_client__main
jumpscale__autossh__http_proxy
jumpscale__base__main
jumpscale__jsagent__main
jumpscale__nginx__main
jumpscale__nodejs__main
jumpscale__osis_client__jsagent
jumpscale__osis_client__main
jumpscale__portal_client__cbportal
jumpscale__portal_client__cloudbroker
jumpscale__portal_client__main
jumpscale__portal_lib__main
jumpscale__python_portal__main
jumpscale__redis__system
jumpscale__statsd-collector__main
openvcloud__cb_cpunode_aio__main
openvcloud__compute_kvm_base__main
openvcloud__compute_node__main
openvcloud__libcloudlibvirt__main
openvcloud__openvstorage__main
openvcloud__openwrt-remote-manager__main
openvcloud__ovs_alba_oauthclient__main
openvcloud__ovs_branding__main
openvcloud__scaleout_networkconfig__main
openvcloud__vfwnode__main
openvcloud__vncproxy__main
```

Since there are typically no services running locally on ovc_git:
- No other sub directories exist under `/opt` apart from `code` and `jumpscale7`
- Under `jumpscale` the directory with the AYS recipes `/opt/jumpscale7/hrd/apps` is empty

...


### Files on ovc_master

Under `/opt/jumpscale7` there is the sub directory `/opt/jumpscale7/hrd/apps` containing all configuration files of the locally installed applications:

```
root@ovcmaster:/opt/jumpscale7/hrd/apps# ls -1
jumpscale__agentcontroller__main
jumpscale__agentcontroller_client__main
jumpscale__base__main
jumpscale__grafana__main
jumpscale__grafana_client__main
jumpscale__gridportal__main
jumpscale__influxdb__main
jumpscale__influxdb_client__main
jumpscale__jsagent__main
jumpscale__mailclient__main
jumpscale__mongodb__main
jumpscale__mongodb_client__main
jumpscale__nginx__main
jumpscale__nodejs__main
jumpscale__oauth_client__oauth
jumpscale__osis__main
jumpscale__osis_client__jsagent
jumpscale__osis_client__main
jumpscale__osis_eve__main
jumpscale__portal__main
jumpscale__portal_client__cloudbroker
jumpscale__portal_client__main
jumpscale__portal_lib__main
jumpscale__python-cloudlibs__main
jumpscale__redis__system
jumpscale__singlenode_grid__main
jumpscale__singlenode_portal__main
jumpscale__statsd-collector__main
jumpscale__statsd-master__main
jumpscale__web__main
openvcloud__billingengine__main
openvcloud__billingenginelib__main
openvcloud__cb_master_aio__main
openvcloud__cbportal__main
openvcloud__cloudbroker__main
openvcloud__cloudbroker_jumpscripts__main
openvcloud__cloudbroker_model__main
openvcloud__cloudbrokerlib__main
openvcloud__libcloudlibvirt__main
openvcloud__libvirtsizes__main
openvcloud__ms1_frontend__main
openvcloud__oauthserver__main
openvcloud__portal_branding__main
openvcloud__vfwmanager__main
```

Next to `/opt/jumpscale7` and `/opt/code` following sub directories exist under `/opt/`:
- grafana
- influxdb
- mongodb
- nginx
- nodejs
- OpenvStorage
- statsd-collector
- stats-master

...


### Files on ovc_reflector

(@TODO)


### Files ovc_dcpm

(@TODO)


### Files ovc_proxy

(@TODO)
