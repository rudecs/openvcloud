# Migaration Script Details

## Prerequisites

 - An installed Kubernetes cluster with ovc deployed docs for that are available [here](Installation.md).
 - A target to migrate from.
 - ssh/0-access access to one of the controller nodes
 
 
## Using the script

The script can be used for both backing up the data into a tar file and uploading that into a webdav server, but can also be used to download and load that tar file into the new enviroment.

The script([here](../scripts/install/backup)) has the following flags:

  --`save`:         create backup and upload to webdav                      
  --`load`:         download backup from webdav and restore into system     
  --`url` :    url to download/upload the backup to                    
  --`no-mongo`:    apply/donotapply action on Mongo database               
  --`no-billing`:  apply/donotapply action on billing files                
  --`date`:   date to restore from with format: month-day-year        


### saving the data
--------------------
To save and upload the cluster data, on the old environment ovc_master docker run the command:

```bash
backup --save --url http://webdav-url/ 
```

This will create a snapshot of mongo and the billing files and add them to a file located at /tmp/backup.tar.gz and then will upload this file to the specified webdav.


### loading the data
--------------------
To download and load the cluster data, on one of the new environment   controllers run the command:

```bash
backup --load --url http://webdav-url/  --date date-backup-made
```

This will download a the tar file from the webdav into /tmp/backup.tar.gz expand the tar file and move the billings to the appropriate place as well as load the mongo database using a Kubernetes job that will terminate once completed.