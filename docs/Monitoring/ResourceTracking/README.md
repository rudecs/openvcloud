# Resource Consumption Tracking

- [How it works](#jumpscripts)
- [Consumption data file format](#capnp)
- [Get the consumption data files using the CloudAPI](#curl)
- [Process the consumption data files](#process-files)
- [Access the consumption data files on the master mode](#access-files)


<a id="jumpscripts"></a>
## How it works

Every hour a consumption data file per account is generated on the master node.

This involves following three Jumpscripts:
- [`aggregate_account_data.py`](https://github.com/0-complexity/openvcloud/blob/master/libs/agent-scripts/resmonitoring/aggregate_account_data.py): aggregates data from all locations that it gets by executing `collect_account_data.py` on the controller of each location, and stores the result on the master
- [`collect_account_data.py`](https://github.com/0-complexity/openvcloud/blob/master/libs/agent-scripts/resmonitoring/collect_account_data.py): per location this script runs on the controller to get the actual data for each account
- [`resmonitoring.py`](https://github.com/0-complexity/openvcloud/blob/master/libs/agent-scripts/resmonitoring/resmonitoring.py): this scripts runs on the controller and stores the data on the controller, this data is afterwards collected by the `collect_account_data.py` script


<a id="capnp"></a>
## Consumption data file format

Every hour a [Cap’n Proto (capnp)](https://capnproto.org/) file per OpenvCloud account with following schema will be generated on the OpenvCloud master node:
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


<a id="curl"></a>
## Get the consumption files using the CloudAPI

Through the [OpenvCloud CloudAPI](/docs/API/README.md) you can download the consumption files for a given account as a zip file.

Here is how to do it using cURL:
```bash
APP_ID="..."
SECRET="..."

IYO_URL="https://itsyou.online/v1/oauth/access_token"
JWT=`curl -d "grant_type=client_credentials&client_id=${APP_ID}&client_secret=${SECRET}&response_type=id_token" ${IYO_URL}`

BASE_URL="https://be-gen-1.demo.greenitglobe.com"
ACCOUNT_ID=<...>

# Specify the start and end time in epoch format, see https://www.epochconverter.com/ for a converter
START=1211507665
END=$(date +%s)

curl -X GET -L --header 'Accept: application/octet-stream'  -H "Authorization: bearer $JWT" ${BASE_URL}'/restmachine/cloudapi/accounts/getConsumption?accountId='${ACCOUNT_ID}'&start='${START}'&end='${END} -o "${ACCOUNT_ID}_${START}.zip"
```

<a id="process-files"></a>
## Process the consumption data files

In case the unzip command isn't yet available on your system, first install it:
```bash
sudo apt-get install unzip
```

Unzip the consumption file:
```bash
export DESTINATION_FOLDER="/tmp/data"
mkdir ${DESTINATION_FOLDER}
unzip ${ACCOUNT_ID}_${START}.zip -d ${DESTINATION_FOLDER}
```

As an example you can check the [export_accounts_xls.py](export_accounts_xls.py) demo script that processes all capnp files it finds in `account/year/month/day/hour` and converts it into an Excel document.


- First make sure you have the **python-xlwt** package installed:
  ```shell
  pip install xlwt
  ```  

- Get the `export_accounts_xls.py` script - requires access to the [0-complexity/openvcloud](https://github.com/0-complexity/openvcloud) repository:
  ```bash
  curl https://raw.githubusercontent.com/0-complexity/openvcloud/master/docs/Monitoring/ResourceTracking/export_accounts_xls.py?$RANDOM > ${DESTINATION_FOLDER}/export_accounts_xls.py
  ```

- Get the `resourcemonitoring.capnp` schema - requires access to the [0-complexity/openvcloud](https://github.com/0-complexity/openvcloud) repository:
```bash
  curl https://raw.githubusercontent.com/0-complexity/openvcloud/master/libs/CloudscalerLibcloud/CloudscalerLibcloud/schemas/resourcemonitoring.capnp?$RANDOM > ${DESTINATION_FOLDER}/resourcemonitoring.capnp
```

- Then execute the script:
  ```shell
  cd ${DESTINATION_FOLDER}
  ipython export_accounts_xls.py
  ```

This will generate an Excel document containing a tab for each account with the resource tracking details per cloud space:

![](xls.png)


<a id="access-files"></a>
## Access the consumption data files on the master mode 

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
