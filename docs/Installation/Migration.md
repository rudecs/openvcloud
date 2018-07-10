# Migrate Older OpenvCloud Environments

This document describes the manual procedure to migrate an existing OpenvCloud master node and controller to a new setup based on a Kubernetes cluster. This will work for both Kubernetes clusters and older installations which only use Docker containers and AYS.

Also see [Migaration Script Details](Migration-script.md).

## Prerequisites

 - An installed Kubernetes cluster with the OpenvCloud pods deployed
 - Source to migrate from
 - `kubectl` connection to the new cluster
 - In case the source uses the old architecture an SSH connection is required to the master node

## Migrating the data

There are three data sources that need to be migrated:
 - [MongoDB](#mongodb)
 - [InfluxDB](#influxdb)
 - [Billing files](#billing)


<a id="mongodb"></a>
### MongoDB

Since MongoDB starting with version 2.3.0 is deployed in a Kubernetes pod, you'll need establish a connection to the Docker container in order to be able to interact with it, this is done as follows:
```bash
    kubectl exec -it <one of the three pod names> /bin/bash
```

Steps to migrate the database:  
1. Export the data in a directory structure on the source master node where the MongoDB server is running:
```bash
    mongodump --out /<path to backup>/`date +"%m-%d-%y"`
```
   Or to a remote machine from which the source MongoDB server is reachable:
```bash
    mongodump --host <bind to old mongo> --port <port to old mongo> --username <username> --password <password>  --out /<path to backup>/`date +"%m-%d-%y"`
```

2. Move the exported data, optionally compressed as a 'tar' or 'zip' file, to a location from which the new MongoDB is reachable, using either a physical carrier such a portable storage device or through the network using `scp`, `rsync` or `ftp`.

3. After ensuring new MongoDB server is running, restore the database, using the following command, pointing to the parent directory where the data is located:
```bash
    mongorestore --drop /<fullpath to location>/<date backup was created>/
```

<a id="influxdb"></a>
### InfluxDB

This database is where statistics are stored. The approach to moving the data is similar to the approach used for MongoDB.

As with MongoDB first make sure you have a connection to the MongDB container:
```bash
    kubectl exec -it <pod name> /bin/bash
```

Steps to migrate the database:
1. Export the data:
```bash
    influxd backup -database statistics <path-to-backup>
```
or
```bash
    influxd backup -database statistics -host <remote-node-IP>:8088 <path-to-backup>
```

2. Move, optionally compressed, the exported data to the location from with the new InfluxDB is reachable

3. Restore the data:
```bash
    influxd restore -datadir <path-to-meta-or-data-directory> <path-to-backup>
    sudo chown -R influxdb:influxdb /var/lib/influxdb
```

InfluxDB can now be restarted.


<a id="billing"></a>
### Billing files

Another vital data source are the billing files which are present on the master nodes. 

Since the billings data is stored inregular files organized in a directory structure per account and time period, you simply need  "tar" or "zip" then and move and extract them without any preprocessing or postprocessing.

For OpenvCloud versions prior to and including 2.2.6 the billing files were stored on master node, under `/opt/jumpscale7/var/resourcetracking`.

Since version 2.3.0 the billing files are still stored on the master node, but under `/var/ovc/billing/`.