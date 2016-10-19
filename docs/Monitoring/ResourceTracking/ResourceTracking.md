## Resource Tracking

On the **ovc_master** virtual machine of your environment every hour the system will generate **Cap’n Proto** (capnp) file with following schema:

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

For the most actual schema you'll need access to the [0-complexity/openvcloud] repository:
https://github.com/0-complexity/openvcloud/blob/2.1.5/libs/CloudscalerLibcloud/CloudscalerLibcloud/schemas/resourcemonitoring.capnp

This will be done in the directory `/opt/jumpscale7/var/resourcetracking`

In order to access these records go through following steps:

- Make sure your private SSH key is loaded:
  ```shell
  ssh-add -l
  ```

- Clone the environment repository:

  ```shell
  git clone %address-of-the-master-copy-of-your-environment-repository%
  ```

- Get the public IP address of **ovc_git** from `services/openvcloud__git_vm__main/service.hrd`

- Make sure **git_root**, the file holding the private key of **ovc_git** is protected:

  ```shell
  chmod 600 keys/git_root
  ```

- Get to the **ovc_git** machine:

  ```shell
  ssh root@%ovc-git-address% -A -i keys/git_root
  ```

- From there it is simple to get on **ovc_master**:

  ```shell
  ssh master
  ```  

- Get to the resource tracking records:

  ```shell
  cd /opt/jumpscale7/var/resourcetracking/%account-ID%
  ```

For each account there will be a subdirectory, for instance for the account with ID 60 this is `/opt/jumpscale7/var/resourcetracking/6`

In there you'll find further subdirectories structured as `year/month/day/hour`.

Using for instance the **export_accounts_xls.py** tool you can convert the capnp file to Excel:
https://github.com/0-complexity/openvcloud/blob/2.1.5/scripts/demo/export_account_xls.py
