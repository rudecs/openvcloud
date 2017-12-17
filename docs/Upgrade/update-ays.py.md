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
Usage: update-ays.py [options]

Options:
  -h, --help            show this help message and exit
  -s, --self            only update the update script
  -r, --restart         only restart everything
  -R, --restart-nodes   only restart all the nodes
  -N, --restart-cloud   only restart all the cloudspace vm
  -n CONCURRENCY, --concurrency=CONCURRENCY
  -u, --update          only update git repository, do not restart services
  --noupdate            if combined with normal update this will only restart
                        services not update them
  --node=NODE           Apply action on this node only
  -U, --update-nodes    only update node git repository, do not restart
                        services
  -C, --update-cloud    only update cloudspace git repository, do not restart
                        services
  -p, --report          build a versions log and update git version.md
  -c, --commit          commit the ovcgit repository

  Update version:
    --tag-js=TAG_JS     Tag to update JumpScale to
    --tag-ovc=TAG_OVC   Tag to update OpenvCloud to
    --branch-js=BRANCH_JS
                        Branch to update JumpScale to
    --branch-ovc=BRANCH_OVC
                        Branch to update OpenvCloud to
    --branch-ovc-core=BRANCH_OVC_CORE
                        Branch to update OpenvCloud to
    --branch-ovc-selfhealing=BRANCH_OVC_SELFHEALING
                        Branch to update OpenvCloud to
```

Keep in mind for what follows that:
- The upgrade script will only work when executed from ovc_git, see the [How to Connect to an OpenvCloud Environment](../Sysadmin/connect.md) section.
- You first need to change the current directory to the directory where all cloned repositories reside, e.g. for environment du-conv-1 this is `/opt/code/git/openvcloudEnvirnement/du-conv-1`

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
