# Installer Script Details

The [installer](../scripts/install/installer) script is used to:
- Setup the Kubernetes cluster on the controller nodes and deploy the OpenvCloud system containers on the Kubernetes cluster
- Install JumpScale services on the OpenvCloud cluster nodes
- Execute IPMI and JumpScale commands on the OpenvCloud cluster nodes
- Deploy virtual machine images

The script is used as follows:
```bash
installer --version {installation version} --config {system config file path} <command> <subcommand> [other options]
```

With `--version` you specify the required release to be installed, e.g. ` 2.3.0`; for all releases check [here](https://github.com/0-complexity/home/tree/master/manifests.

With `--config` you specify the path to the system configuration file, typically `/system-config.yaml`. This file contains all the necessary information for a successful installation using the YAML format. For more details see [Configuration File Details](System-config.md).

The script takes following commands:
- [cluster](#cluster)
- [node](#node)
- [storage](#storage)
- [image](#image)


<a id="cluster"></a>
## cluster

The `cluster` command is used to perform actions on the Kubernetes cluster which includes deploying, updating and upgrading the Kubernetes cluster and its workloads.

There are four `cluster` subcommands:
- [cluster deploy](#cluster-deploy)
- [cluster resources](#cluster-resources)
- [cluster updatedomain](#cluster-updatedomain)
- [cluster upgrade](#cluster-upgrade)


<a id="cluster-deploy"></a>
### cluster deploy

The command `cluster deploy` will use the **JumpScale Prefab module for Kubernetes** to install the Kubernetes cluster and deploy the OpenvCloud pods.

Following options are available
- `--configure-cluster` specifies to setup the Kubernetes cluster or not
- `--no-configure-cluster` specifies to only OpenvCloud pods

Usage

``` bash
    installer --config system-config.yaml cluster deploy
```

<a id="cluster-resources"></a>
### cluster resources

The `resources` command is used to handle Kubernetes resource files.

There are four `cluster resources` subcommands:
- [`apply`](#cluster-resources-apply)
- `applyall`     Apply all kubernetes resources
- `write`        Rewrite all templates
- [`writeconfig`](#cluster-resources-writeconfig)

<a id="cluster-resources-apply"></a>
### cluster resources apply

Apply a specifified kubernetes resource
Following options are available:
- `--path` path to template

<a id="cluster-resources-writeconfig"></a>
### cluster resources writeconfig

The command `cluster resources writeconfig` is used to create Kubernetes **ConfigMaps** from the specified configuration file. `configmap` is the specified configuration that can be mounted to the Kubernetes pods when the application needs information from the config file to perform its operations. This is already handled using the above command but this command can be used if it is required to update the ConfigMap with new config data.

Usage is as follows
- Write or update system-config in Kubernetes ConfigMap based on YAML file:
    ```bash
    installer --config system-config.yaml cluster resources writeconfig
    ```

- Rewrite kube resources from template:
    ```bash
    installer --config system-config.yaml cluster resources write
    ```


<a id="cluster-updatedomain"></a>
### cluster updatedomain

The command `cluster updatedomain` is used to update the SSL certificates and the domain of the environment. This is done by updating the `environment` and/or `certificates` sections in the passed configuration file.
`ssl` section needs to be updated with a new certificate names for the certificate update, the `subdomane` and `basedomain` for the update domain.
If adding a new certificate, `certificates` section needs to be updated with a new certificate, referenced from `ssl` section.

<a id="cluster-upgrade"></a>
### cluster upgrade

 Upgrade cluster, update all nodes and cluster and update kubernetes resources.

<a id="node"></a>
## node

The `node` command is used to execute IPMI and JumpScale actions on the CPU and storage nodes in the OpenvCloud cluster.

Subcommands of `node`:
- `action`    Will apply the action on storage and cpu...
- `jsaction`  Will apply the action on all nodes (cpu,...
- `update`    Update code and restart required services on...


Usage is as follows:
```bash
installer --config system-config.yaml node action --name node_name <action>
```

with `--name` you specify the name of the CPU/storage node, as configured in the configuration file.

Following **IPMI** commands are supported:
- `reboot` reboots the specified node
- `is_up` check whether node is up and running
- `wait_up` waits untill the node is up and running
- `enable_pxe` enables PXE on node
- `disable_pxe` disables PXE on node
- `install_os` installs the operating system on node

Following **JumpScale** commands are supported:
- `install` installs JumpsScale services
- `start` starts JumpScale services
- `stop` stops JumpScale services r
- `restart` restart JumpScale services
- `update` updates JumpScale services


<a id="storage"></a>
## storage

Subcommands:

- `applyconfig`  Apply storage config

<a id="image"></a>
## image

The `image` command is used to install virtual machine images on the OpenvCloud cluster.

Usage is as follows:
```bash
installer --config system-config.yaml image deploy --name image_name
```

With `--name` you specify the AYS template of the image package to deploy.


