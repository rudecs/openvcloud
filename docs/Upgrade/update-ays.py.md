## Using update-ays.py

Updating the master cloud space and all the CPU nodes can be achieved with one script: `update-ays.py`.

This script is available from the `scripts/updates` directory in the [OpenvCloud](https://github.com/0-complexity/openvcloud) repository.

The update script will help you doing some tasks like:
- Self-updating the update script
- Perform a complete update
- Only update the master cloud space machine repositories
- Only update the CPU node repositories
- Only restart master cloud space services
- Only restart CPU node services
- Update the `version.md` file
- Commit the local `openvcloudEnvironement` directory to gitlab

Here are all available options listed:
```
  -s, --self           self update: only update the update script
  -r, --restart        restart everything (master cloud space and all CPU nodes)
  -R, --restart-nodes  restart all the CPU nodes
  -N, --restart-cloud  restart all the master cloud space services
  -u, --update         update git repository (do not restart services)
  -U, --update-nodes   update node git repository (do not restart services)
  -C, --update-cloud   update the master cloud space git repository (does not restart services)
  -p, --report         build a versions log and update git version.md
  -c, --commit         commit the ovc_git repository
```

Keep in mind for what follows that:
- The upgrade script will only work when executed from ovc_git, see the [How to Connect to an OpenvCloud Environment](../Sysadmin/connect.md) section.
- You first need to change the current directory to the directory where all cloned repositories reside, e.g. for environment du-conv-1 this is `/opt/code/git/openvcloudEnvirnement/be-conv-1`

> Don't forget to first update the update script itself, which can be achieved with:

```
jspython .../update-ays.py --self
```

The full update process, both updating the master cloud space and all the CPU nodes, can be started with one single command:

```bash
jspython /opt/code/git/0-complexity/openvcloud/scripts/updates/update-ays.py
```

Or alternatively you can first update all cloned repositories and then restart all services:

```
jspython .../update-ays.py --update
jspython .../update-ays.py --restart
```

Next you will want to [commit the changes and report back to the master repository](../CommitChanges/CommitChanges.md).