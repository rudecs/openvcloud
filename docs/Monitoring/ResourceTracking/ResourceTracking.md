## Resource Tracking

On the **ovc_master** Docker container a **Cap’n Proto** (capnp) file with following schema will be generated every hour:

```
@0x934efea7f327fff0;
struct CloudSpace {
  cloudSpaceId @0 :Int32;
  accountId @1 :Int32;
  machines @2 :List(VMachine);
  state @3 :Text;
  struct VMachine {
    id @0 :Int32;
    type @1 :Text;
    vcpus @2 :Int8;
    cpuMinutes @3 :Float32;
    mem @4 :Float32;
    networks @5 :List(Nic);
    disks @6 :List(Disk);
    imageName @7 :Text;
    status @8 :Text;
    struct Nic {
      id @0 :Int32;
      type @1 :Text;
      tx @2 :Float32;
      rx @3 :Float32;
    }
    struct Disk {
        id @0 :Int32;
        size @1 :Float32;
        iopsRead  @2 :Float32;
        iopsWrite  @3 :Float32;
        iopsReadMax @4 :Float32;
        iopsWriteMax @5 :Float32;
    }
  }
}

struct Account {
  accountId @0  :UInt32;
  cloudspaces @1 :List(CloudSpace);
}
```

Get access to the [0-complexity/openvcloud](https://github.com/0-complexity/openvcloud/blob/2.1.5/libs/CloudscalerLibcloud/CloudscalerLibcloud/schemas/resourcemonitoring.capnp) repository for the most up to date schema.

In order to get access to **ovc_master** you first need to get access to one of the controllers of your G8 environment:

- Check whether your private SSH key is loaded:

  ```shell
  ssh-add -l
  ```

- In case your private key is not loaded, let's add it by first making sure **ssh-agent** is running, and then actually adding the key:

  ```shell
  eval $(ssh-agent)
  ssh-add ~/.ssh/id_rsa
  ```

- Clone the environment repository:

  ```shell
  git clone %address-of-the-master-copy-of-your-environment-repository%
  ```

- Get the (public) IP address of one of the controllers from **service.hrd** in **services/openvcloud__ovc_setup__main**:

  ```shell
  cat services/services/openvcloud__ovc_setup__main/service.hrd
  ```

- The IP address will be found as a value for **instance.ovc.cloudip**

- Make sure **master_root**, the file holding the private key for accessing the controller is protected:

  ```shell
  chmod 600 keys/git_root
  ```

- Get to the controller over SSH:

  ```shell
  ssh root@%ovc-git-address% -A -i keys/git_root
  ```

Now that you are connected to one of the controllers, you will access the **ovc_master** Docker container:

- On the controller you might first want to list all running Docker containers:

  ```shell
  docker ps
  ```

- The **ovc_master** Docker container will be listed as one of the running containers, start an interactive session with it:

  ```shell
  docker exec -i -t ovcmaster /bin/bash
  ```

- Get to the resource tracking records:

  ```shell
  cd /opt/jumpscale7/var/resourcetracking
  ```

For each account there will be a subdirectory, for instance for the account with ID 60 this is `/opt/jumpscale7/var/resourcetracking/6`

In there you'll find further subdirectories structured as `year/month/day/hour`.

Using for instance the **export_accounts_xls.py** demo script you can convert the cpnp files to an Excel document:

```shell
cd /opt/code/github/0-complexity/openvcloud/scripts/demo
python3 export_accounts_xls.py
```

This will generate an Excel document containing a tab for each account with the resource tracking details per cloud space:

![](xls.png)
