## Update Open vStorage

Updating Open vStorage is more tricky than updating OpenvCloud.

You can find the update script in the same folder as where `update-ays.py` resides, called `update-ovs.py`

The update script will help you doing some tasks like:
- Check if updates are available
- Do an apt-get update on each node
- Do some pre/post-process actions to put environment in a stable condition to perform the update
- Update Open vStorage Framework
- Update Open vStorage Volume Driver
- Update Open vStorage ALBA (backend)
- Update Open vStorage Arakoon cluster
- Stop/start all running virtual machines

Here are all available options listed:
```
  -c, --check         check for update
  -u, --update        just run apt-get update on each nodes
  -P, --preprocess    runs some pre-upgrade commands
  -S, --postprocess   runs some post-upgrade commands
  -r, --arakoon       attempt to update only arakoon
  -o, --framework     attempt to update only ovs-framework
  -v, --volumedriver  attempt to update only volumedriver
  -a, --alba          attempt to update only alba backend
  -s, --sync          sync apt-get archives directory (download faster)
  -O, --stop-vm       stop all running vm
  -A, --start-vm      start previously stopped vm
  -k, --skip-vm       do not start/stop vm during update
```

Notes:

- Since this file is in the same repository as the `updaye-ays.py` script, there is no `--self` option, please use `update-ays.py` to update it.
- here is no "all-in-one" process like `update-ays.py` because you **need** to be careful with this process, some mistake can break lot of stuff in your storage system.

### What's inside

First, some explanation:
- **Open vStorage Framework**: this part of the package doesn't need to take down your storage system to perform the update, it's a software part between storage and management
- **Open vStorage Volume Driver**: this part needs a complete shutdown of all running virtual machines since it needs to restart and this job take care about the sharing system
- **Open vStorage ALBA**: this part needs a complete shutdown too because it touches the manager of the physical disks of your setup
- **Open vStorage Arakoon Cluster**: this part takes care about the "index" of files, it doesn't need a complete shutdown

With this background information, you can now update some parts (or all parts), depending of your need.

Note: just as is the case with `update-ays.py`, keep in mind for what follows that:
- The upgrade script will only work when executed from ovc_git
- You first need to change the current directory to the directory where all cloned repositories reside, e.g. for environment du-conv-1 this is `/opt/code/git/openvcloudEnvirnement/be-conv-1`

### Update repositories

First thing to do is update the cloned repositories, execute the following command:
```
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --update
```

When done, you can check which updates are available:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --check
```

The output will be like:
```
[+] update for arakoon: False
[+] update for framework: True
[+] update for volumedriver: True
[+] update for alba: False
```
Which means that there is an update available for **Framework** and **Volume Driver**, the rest is up-to-date.

### Upgrading parts

The default action when updating **ALBA** and **Volume Driver** will stop then start all running Virtual Machines. You can avoid this default behavior with `--skip` option during update. This is useful when you want to update multiple part in one shot and moreover, you can have a better control of what you do.

To prevent any action (create, delete vm, ...), you can put your storage system "Offline" by starting the `pre-process` part:

```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --preprocess
```

To make your system back "Online", when done, run:
```
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --postprocess
```

#### Framework

To upgrade the framework, double check that you are offline (Overview Status of your environment should be "HALTED"), then run:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --framework
```
When done, you should be to the last version of the framework

#### Arakoon

Like the framework, double check you are Offline, then:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --arakoon
```

#### ALBA and Volume Driver

Now these part is more dangerous, we will take the safer way and do it things separately. Like before, double check you are in offline mode, then stop all running virtual machines:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --stop-vm
```

This action will gracefully stop all running Virtual Machines, then save the list of machines to a file (which is in `/tmp/ovs-machine-state.json`). With this file, you can restart all stopped virtual machines after the upgrade to get your system back in the same state as before upgrade.

When everything is down, upgrade **ALBA** or **Volume Driver** as needed:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --skip --alba
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --skip --volumedriver
```

When you're done, restart all virtual machines:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --start-vm
```

Then go back Online:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ovs.py --postprocess
```

Open vStorage should be upgraded !
