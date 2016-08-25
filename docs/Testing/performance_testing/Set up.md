## General Set up of the system
The Performance test repo can be found on github

https://github.com/gig-projects/org_quality.git


To start the performance test 2.0 we should connect to one of the physical nodes of the environment that needs to be tested. To connect to a physical node, follow the steps as described in the [connect documentation](connect.md).

When connecting to a physical node the node will not be used during the stress test. e.g. When you connect to node 1, tests will run on node 2 and other available nodes.

First we need to get the install script on the physical machine on the root directory.
```
git clone https://github.com/gig-projects/org_quality.git
cd org_quality/Environment\ testing/performance\ testing
```

In the folder "Performance_test" there are several files:
- Perf_parameters.cfg  = input file where we define parameters
- README.md  
- scripts  =  contains actual scripts.
- utils

**Perf_parameters.cfg**
The Performance test parameters can be changed in this file.

**scripts**
In this script folder you can see that there are 4 scripts defined

1. collect_results.py  
A script which is made to collect all the results of the virtual machines.

2. Machine_script.py  
This is the script that runs on each virtual machine.

3. setup_test.py  
This is a script for setting up environment and execute the test script.  
4. tear_down.py  
tear down the environment means that you deleting every thing u created including user, accounts, cloudspaces and VMs.

## FIO settings
The FIO is a test that run per specific disk, so the command that used here is excuted per each disk per vm and in a multiprocessing way which means we start running same command on all disks per vm on the same time.
The command used:
fio --ioengine=libaio --direct='1' --gtod_reduce=1 --name=test --size=1000M --readwrite=write --numjobs=3  --directory=/mnt/disk_b

Note: the default block size that is used here is 4k (bs=4k)

--ioengine=libaio --> for Linux native asynchronous I/O

--direct='1'      --> means non buffered IO

--gtod_reduce=1   --> to reduce results for presenting only the important information

--directory=/mnt/disk_b --> from where i will run the command (directory = where the disk is mounted)

--readwrite=write --> Type of I/O pattern (write means sequential write)

--size=1000M      --> the size of the file that will be written

--numjobs=3       --> Number of processes (in this case each process will wirte 1G which means When running the test we are writing 3GB of data per disk )

So this means if we have defined 5 disks per VM we will write 3GB x 5 disk for each iteration.

## VM specs
- cpu cores = 2
- memory = 2048
- boot disk size = 100G
- Number of data disk = 5 , each disk = 30G

 These parameters can be changed in Perf_parameters.cfg file


## Running the test script
Prior to running the script we need to make sure that the environment is clean. To clean the environment we need to use the tear down script.

Connect as root to the physical environment, go to the Performance_test script directory and run the tear_down.py script.

```
cd Performance_test
jspython scripts/tear_down.py --clean
```
Note: --clean option will delete all users except gig and admin users and will remove all accounts except the test_storage account which is responsible for checking environment health periodically

Now need to set up the required parameters.To change the performance test parameters we need to run a vim command.
```
vim Perf_parameters.cfg
```
Following paramenters are available in the file:
```
 [perf_parameters]

# Number of Iterations --> each iteration create one VM per cpunode(stack)
iterations: 1

# No of cloudspaces --> an account is created for each cloudspace and Number of cloudspaces should be less than or equal that of cpu nodes
No_of_cloudspaces: 2

# Number of cpu nodes which will be used for the test (must be less than environment_cpu_nodes-1 )
used_stacks: 3

# Parameters required for VM
# RAM and cpu are coupled together,
# please choose between these values [RAM, vcpu] = [512,1] or [1024,1] or [4096,2] or [2048,2] or [8192,4] or [16384,8]
# RAM specifications
memory: 2048
#vcpu cores
cpu: 2

#Boot Disk size (in GB), please choose between these values [10, 20, 50, 100, 250, 500, 1000, 2000] -- default = 100G
Bdisksize: 100

# Number of data disks per VM
no_of_disks: 5

# Data disksize per vm
data_disksize: 30



# Parameters required for FIO
# FIO starting time difference between virtual machines (in seconds)
vms_time_diff: 10

# Test-rum time per virtual machine  (in seconds)
testrun_time: 300

# Amount of data to be written per each data disk per VM (in MB)
data_size: 3000

# Type of I/O pattern -- what you will enter will be the same for all VMs (enter:
# 'write' for sequential write or 'randwrite' for random write
# 'read' for sequential read or 'randread' for random read
# 'rw' for mixed sequential reads and writes or 'randrw' for mixed random reads and writes
# if you enter nothing then half of the vms will be write and the other half will be randwrite
IO_type: write



# Results Directory : write absolute directory
Res_dir: /perftest

# username
username: perftestuser

# should run all scripts from inside the repo

```
Now from inside the Repo run the test script
```
jspython scripts/setup_test.py
```
Note: after running the setup_test.py and investigating the environment (if needed), please make sure
to tear down the environment

When setup_test.py is completed, a user is created, a cloudspace is made, vms are created, disks are mounted and FIO testing is done.

*user information*  
username: perftestuser (can be changed in the Perf_parameters.cfg)
PW: gig12345

*Cloudspace information*
For each cloudspace, an account is created
name of the deployed cloudspace = default

*vm information*  
During the testscript vm's are created following the naming convention  

"nodexy"   
x = the stack where the vm is installed

y = the iteration number  

Each deployed vm also gets his own ID during the set up.  

The more iterations we have selected the more vm's are created per node or stack. This means if you have 3 iterations selected and we use 1 stack in the set up we have the following process:

Iteration 1:
- A vm created on stack 1 and FIO test is done, let's call it vm1.

Iteration 2:
- A new vm is created on stack 1 and FIO tests are now performed on vm1 and vm2

Iteration 3:
- A new vm is created on stack 1 and FIO tests are now performed on vm1, vm2 and vm3.


## Check the test results.
If we want to check the results of the test we need to open the following file:  
```
cd /perftest/
vim total_results
```
In the test result file we can view the following information in total_results file
the results are presented per vm per iteration
- total IOPS
- Avg_cpuload
- test runtime: time taken to run the test

Also you can find the sum up of all these informations printed in a pretty table
in a file called total_results.table

Concerning the VMs creation time (the time from creating a vm till it take an ip and we have SSH access), the results for all VMs can be found in a file called
```
cd /perftest/
VMs_creation_time.txt
```
