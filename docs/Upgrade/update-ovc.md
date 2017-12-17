## Full OpenvCloud Update

- Connect to the ovc_git node with your ssh-agent forwarded.  
- Change your `pwd` to your environment directory ex. `/opt/code/github/gig-projects/env_du-conv-1`  
- Update the update script.
- Update all the rest
- Now login to the ovc_master node and execute the upgrader/migration script with the correct verion.

Full Example:

```
# ssh in the first controller
ssh -A -p 34022 gig@du-conv-1.demo.greenitglobe.com
# ssh into the ovc_git
ssh -A -p 2202 root@loalhost
cd /opt/code/github/gig-projects/env_du-conv-1
#update the update script
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --self --branch-js=production --branch-ovc=production
# update the nodes
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --branch-js=production --branch-ovc=production
# switch to the ovc_master
exit
# the port for ovc_master might vary double check the hostname
ssh -p 9022 root@localhost
# run the migration/upgrade script passing the correct version along
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/upgrader.py -v 2.2.3

```
