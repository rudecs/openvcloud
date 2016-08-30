## Post Installation Steps


### Images

Now you are ready to deploy a VM image:
```
ays install -n image_ubuntu-1404-x64 --targettype node.ssh --targetname $NODENAME
```

Replace `$NODENAME` by a node name (eg: be-conv-1-01)


### Sync the image to the other nodes

1. Go to the **Cloud Broker Portal**
2. Go to **Locations**
3. Select the location
4. Click on Choose action
5. Click on Sync available images to cloud broker
6. Go to the **Cloud Broker Portal** again
7. Select the image
8. Click on Choose action
9. Choose Image availability
10. Select all nodes


### Sync the sizes to the other nodes

1. Go to the **Cloud Broker Portal**
2. Go to **Locations**
3. select location
4. clock on choose action
5. click sync available sizes to cloudbroker


### Create an account/username 

1. Go to the **Cloud Broker Portal**
2. Go to **Users**
3. Add user
4. Go to **Accounts**
5. Add account


### Deploy your first Machine
1. Go to the **End User Portal**
2. Go to **Machines**
3. Create your new machine and select the image you just synced
