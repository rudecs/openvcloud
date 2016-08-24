## How to Deploy a New OS Image

### Concept

When a virtual machine is created, some actions need to be done within the guest like resizing of the filesystem, creation of users,...
To accomplish this, [cloudinit](https://cloudinit.readthedocs.io/en/latest/index.html) is used. For most Linux distributions, downloads of 'cloud images' with cloudinit preinstalled are readily available for download. The rest of this page assumes you have have an OS image with cloudinit available. There is a guide on [how to create a windows base image with cloudinit](Creating_new_Windwos_Image.md). 


### Clone the repository of your environment

From a well prepared computer, as documented [here](preparing_for_indirect_access.md), your first step will be to clone the repository of your environment from AYDO to your local (virtual) machine:
```
git clone https://git.aydo.com/openvcloudEnvironments/$name-of-your-env$
```


### Create a new image directory and the AYS service recipe for your new image

For each image there is a directory under `/opt/code/git/openvcloudEnvironments/$name-of-your-env$/servicetemplates`
```
cd /opt/code/git/openvcloudEnvironments/$name-of-your-env$/servicetemplates
```

Let's create an sub directory for the image available from https://cloud-images.ubuntu.com/wily/current/wily-server-cloudimg-amd64-uefi1.img:
```
mkdir image_wily-server
```

Each directory contains 3 files:

- **services.hrd** contains the all required information about ftp server that holds your image

  - **url**: address of your ftp server from where the image is available, e.g. `ftp://pub:pub1234@ftp.aydo.com`
  - **source**: exact location on the ftp server from where the image can be downloaded, e.g. `/images/image_windows2012`
  - **checkmd5**: whether the MD5 checksum needs to be checked, typically 'true'
  - **dest**: directory where the image needs to be downloaded, e.g. `/opt/jumpscale7/var/tmp/templates/image_windows2012.qcow2`

- **actions.py** defines the configure method that will be called to register the image once it got downloaded successfully

  - **name** sets the image name, e.g. 'image_windows2012'
  - **imagename** sets the disk image name as physically saved, e.g. 'image_windows2012.qcow2'
  - **registerImage(serviceObj, name, imagename, category, minimum-image-size)** the actual registration method, where you have two additional parameters:
    - **category** specifies under which category the image will be available to the end user, typically 'Linux' or 'Windows'
    - **minimum-image-size** sets the minimum image size, in case of a windows image you have to set it to at least 20, otherwise 10 is fine for linux images

- **instance.hrd** (leave it empty)

We actually only need to create 2 files, representing the AYS service recipe for this image:
- service.hrd
- actions.py

Staring with `service.hrd`:
```
vi service.hrd
```

Provide following service description, hit `i` to go in edit mode:
```
platform.supported             = 'generic'

web.export.1                   =
    checkmd5:'false',
    dest:'/opt/jumpscale7/var/tmp/templates/wily-server-cloudimg-amd64-uefi1.qcow2',
    source:'/wily/current/wily-server-cloudimg-amd64-uefi1.img',
    url:'https://cloud-images.ubuntu.com',
```

Save and close the new file by first pressing `esc`, typing `:wq` and hitting `enter`.

And now let's create the `actions.py` file:
```
vi actions.py
```

We only need to implement the `configure` method:
```
from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """


    def configure(self, serviceObj):
        from CloudscalerLibcloud.imageutil import registerImage
        name = 'Wily Server 15.10 amd64'
        imagename = 'wily-server-cloudimg-amd64-uefi1.qcow2'
        registerImage(serviceObj, name, imagename, 'Linux', 10)
```

### Save, commit and push your changes to the repo

Add the newly created directory and sub folders to the local git repository:
```
cd /opt/code/git/openvcloudEnvironments/$name-of-your-env$
git config --global push.default simple
git add image_wily-server
git commit -m "new image"
git push
```

### Install the image

From your well prepared computer, as documented [here](preparing_for_indirect_access.md), open an SSH session on the ovc_git machine, don't forget the -A option in order to have the ssh agent forwarding to work:

```
ssh -A -p 2202 root@$ip-address
```

Update the repository:
```
cd /opt/code/git/openvcloudEnvironments/$name-of-your-env
git pull
```

Make the updated servicetemplates directory current:
```
cd /opt/code/git/openvcloudEnvironments/$name-of-your-env$/servicetemplates
```

And finally install the image, make sure to specify the name of one/any of the physical nodes (last option argument):
```
ays install -n image_wily-server --targettype node.ssh --targetname $name-of-a-node-in-your-env$
```

In case you're updating an already previously installed image, use the -r option:
```
ays install -r -n image_wily-server --targettype node.ssh --targetname $name-of-a-node-in-your-env$
```


### Set image availability

In the **Cloud Broker Portal** go to the **Image Details** page for your newly added image and select **Image Availability** from the **Actions** menu:

![](ImageAvailability.png)

Confirm on which nodes you want to make this image available:

![](ImageAvailability2.png)