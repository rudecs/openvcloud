## OpenvCloud Quality Performance Test

This repository contains the complete performance test script.

Performance test reports can be found [here](https://docs.google.com/document/d/1BiSOzdzidArtnuS9oPSdsCgIGE_VczgYvzTGJ_5ys_I/edit?usp=sharing).


### General set up of the system (for FIO test)

The performance tests can be found on GitHub: [here](https://github.com/gig-projects/org_quality/tree/master/Environment%20testing/performance%20testing).
inside the [org_quality repo] (https://github.com/gig-projects/org_quality)


To start the performance test 2.0 we should connect to one of the physical nodes of the environment that needs to be tested. 

When connecting to a physical node the node may be used during the stress test. we can run the tests from any node.

First we need to get the install script on the physical machine on the root directory.
```
git clone git@github.com:gig-projects/org_quality.git
```

In the folder "Performance_test" there are several files:
- Perf_parameters.cfg  = input file where we define parameters
- README.md
- scripts  =  contains actual scripts.
- utils

**Perf_parameters.cfg**
The Performance test parameters can be changed in this file.

**scripts**
In this script folder you can see that there are 5 scripts defined
1. collect_results.py
A script which is made to collect all the results of the virtual machines.
2. core  __init__.py
3. Machine_script.py
This is the script that runs on each virtual machine.
4. setup_test.py
This is a script for setting up environment and execute the test script.
5. tear_down.py
tear down the environment means that you are removing all information on that machine to start clean... So removal of vm's, cloudspaces and the users created.

### FIO settings
When running the test we are writing 3GB of data per disk. This means if we have defined 5 disks we will write 3GB x 5 per iteration.


### Running the test script
Prior to running the script we need to make sure that the environment is clean. To clean the environment we need to use the tear down script.

Connect as root to the physical environment, go to the Performance_test script directory. and run the tear_down.py script.

```
cd Performance_test
jspython scripts/tear_down.py --clean
```
Now we need to set up the required parameters.

To change the performance test parameters we need to run a vim command.
```
vim Perf_parameters.cfg
```
Following paramenters are available in the file:
```
# No. of Iterations : each iteration create one VM per cpunode(stack)
iterations: 1

# No of cloudspaces : an account is created for each cloudspace : No. of cloudspaces should be less than or equal that of cpunodes
No_of_cloudspaces: 1

# number of cpu nodes which will be used for the test (must be less than env_cpu_nodes-1 )
used_stacks: 1


#number of data disks per VM
no_of_disks: 5

# Data disksize per vm
data_disksize: 30

#FIO starting time difference between virtual machines (in seconds)
vms_time_diff: 10

# test-rum time per virtual machine  (in seconds)
testrun_time: 300

# Results Directory : write absolute directory
Res_dir: /perftest

# Parameters required for FIO
# username
username: perftestuser

# should run all scripts from inside el repo
```
Now run the test script
```
jspython scripts/setup_test.py
```
When the complete set up is done a user is created, a cloudspace is made, vm's are created, disks are mounted and FIO testing is has started.

*user information*
username: perftest
PW: gig12345

*vm information*
during the testscript vm's are created following the naming convention

"nodexy"
x = the stack where the vm is installed

y = the iteration number

Each deployed vm also gets his own ID during the set up.

The more iterations we have selected the more vm's are created per node or stack. This means if you have 3 iterations selected and we use 1 stack in the set up we have the following process:

Iteration 1:
- vm created on stack 1 and FIO test is done.

Iteration 2:
- a new vm is created on stack 1 and FIO tests are now performed on vm1 and vm2

Iteration 3:
- a new vm is created on stack 1 and FIO tests are now performed on vm1, vm2 and vm3.

- Note: you can change the number of vms created per stack per iteration in the parameters file.

### Check the test results
If we want to check the results of the test we need to check the following file:
```
cd /org_quality/Environment_testing/tests_results/FIO_test/(date)_(cpu_name).(env_name)_testresults(run_number)/
vim (date)_(cpu_name).(env_name)_testresults(run_number).csv
```
In the test result file we can view the following information
- Total IOPS per vm per Iteration
- Avergage cpu

----------------------------------------------------
## This test has also been divided into 2 scripts :
  1- demo_create_vms.py: create all vms on the environment  
  2- demo_run_fio.py: runs FIO tests on all vms inn parallel  

- These scripts assuming that all machines are created on one cloudspace  

- Precautions

  1- After creating the vms please make sure that the assigned ip for the machines
     matches the ip on the portal  

- To Run the scripts

  1- cd org_quality/Environment_testing/performance\ testing/  
  2- jspython scripts/demo_create_vms.py 25 (25 = number of vms need to be created)  
  3- jspython scripts/demo_run_fio.py 10 (10 = number of vms need to run FIO on .. (bet (1-25))  

