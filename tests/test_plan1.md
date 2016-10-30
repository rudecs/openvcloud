# New features test plan (26 Oct 2016)
This is only a start plan which can be extended later on while more understanding each feature requirements.
 
Prepared by:
	(Ramez Saeed) 
	(26 Oct 2016)

## TABLE OF CONTENTS
    1.0  INTRODUCTION                         
    2.0  OBJECTIVES AND TASKS                         
        2.1  Objectives                                         
        2.2  Tasks                         
    3.0  SCOPE                                 
    4.0  Features to Be Tested     
    5.0  Testing Strategy                                                  
        5.1  System and Integration Testing                 
        5.2  Performance and Stress Testing                                                              
    6.0  Environment Requirements                                                                                                                      
    7.0  Resources/Roles & Responsibilities                                   
    8.0  Dependencies
    9.0  RISKS/ASSUMPTIONS
                                 
###1.0 INTRODUCTION
This test plan is a high level test overview for the mentioned new features,
more details about the test steps itself should be added in the future when have more info about
each feature and try them manually.
 
###2.0 OBJECTIVES AND TASKS
####2.1    Objectives
	create test coverage for all the mentioned new features.

####2.2    Tasks
	https://github.com/gig-projects/org_quality/issues/509

###3.0 SCOPE
	Functional testing
	Performance testing (@Geert: please provide which fields need to be tested and what/how is the expected result for them)

### 4.0 FEATURES TO BE TESTED
	1- Limit machine disk IOPS
	2- Resources management
	3- External networks
	4- Import/Export machine features

### 5.0 TESTING STRATEGY
	we need to use the cockpit and AYS blue prints to drive test in these features.
	
	## install cockpit
	- We need to install a stable cockpit somewhere to be used for drive test suites (Ex. be-scale-3)
		https://gig.gitbooks.io/cockpit/content/installation/installation.html

	## testing
	- we need to write the test which will be run through blue prints on the cockpit.
	There should be a configurable blue print which points out to the the environment to test.

	## AYS templates
	- For every script that we are running we need to create an AYS template. For the moment we have several AYS templates which can be re-used.

	## using REST APIs
	- this script can be used to call all the system REST APIs in order to check, verify and assert the results will come out from the blue prints:
		https://raw.githubusercontent.com/grimpy/openvcloudash/master/openvcloudash/openvcloud/client.py
		```
		client = Client(url, login, password)
		client.system.health.getOverallStatus()
		client.cloudapi.accounts.list()

		```
### 5.1    System and Integration Testing
	
	1- Limit machine disk IOPS:
		test1:
			1. create a blueprint to add (account, CS, VM) and deploy
			2. run fio test, store result
			3. edit blueprint to limit the IOPS of the VM and deploy
			4. run fio test, validate result against last deployed blueprint
			5. add a new disk to the VM in the blueprint, limit its IOPS and deploy
			6. run fio test, validate result against last deployed blueprint
			7. decrease the IOPS limits in the blueprint and deploy
			8. run fio test, validate result against last deployed blueprint
				
	2- Resources management
		Reference:
		https://github.com/0-complexity/selfhealing/blob/master/specs/resource-usage-tracking.md

		test1:
			1. create a blueprint to add (1 account, 2 CS, 4 VM)
			2. check what should be the time to wait until the bin file is created on master node
			3. download this bin file using API commands and assert all the info inside it are correct.
				this script can be used to read the bin file data:
				/opt/code/github/0-complexity/openvcloud/scripts/demo/export_account_xls.py
			4. update the blueprint to add more VMs
      5. download the new bin file using API commands and assert all the info inside it are correct.
			expected result: all the data should be aggregated to the master node under directory has the name of the account ID.

		test2:
			1. create a blueprint to add (1 account, 1 CS, 1 VM)
      2. test Upstream aggregation time (don't know how to do that yet, need to try it manually first)
		test3:
			1. create a blueprint to add (2 account, 4 CS, 8 VM)
      2. update the blueprint to destroy 1 account and 1 CS and 1 VM
      3. download the new bin file using API commands and assert all the info inside it are correct.
      4. update the blueprint to disable 1 account
      5. download the new bin file using API commands and assert all the info inside it are correct.
	
	3- External networks
		test1:
			1. create a blueprint to create 1 CS with multiple networks
         (still need more info how to do that as there are no docs for this feature)
      2. check the CS had been created.
      3. update the bluprint to create 1 VM for each network.
		test2:
			1. create blueprint to add one account with two different types of networks
			2. update blueprint to create a cloud space with specific network (pivate one)
			3. update blueprint to create two VMs
      4. assert that they can talk to each other via the private network
		test3:
			1. create a blueprint to assign a network to specific account (@Jo: please update us with more info how we can do that)

	4- Import/Export machine features
		Reference:
			https://github.com/0-complexity/openvcloud/blob/2.1/specs/import-export-virtual-machines.md
		test1:(import test)
			1. have access to owncloud so the test can import VMs
			2. create bluprint to add VM and upload ovf to owncloud
			3. on G8 Env update the blueprint to import the uploaded Vm with all the needed params in the specs
			4. assert that G8 performs the import and sends results via email to the user

		test2: (export test)
			1. have access to owncloud so the test can export VMs
			2. on G8 Env create bluprint toexport Vm with ID and path all the needed params in the specs
			3. assert that G8 performs the export and sends results via email to the user


### 5.2    Performance and Stress Testing
	1- Limit machine disk IOPS:
		Edit the performance existing FIO test to set the IOPS on disks and check the changes, expected that with each IOPS decrease the Env should handle more IOPS on different VMS.

### 6.0 ENVIRONMENT REQUIREMENTS
	1- Virtual machine to have the cockpit installed.
	2- test environment has all the new features installed and updated.


### 7.0 RESOURCES/ROLES & RESPONSIBILITIES
	QA team members who are involved in this:
		Ramez Saeed
		Islam Taha

### 8.0 DEPENDENCIES
	- stable cockpit deployment and installation
	- stable AYS installation
	- support from the development team to help adding AYS templates as per tests requirements

### 9.0 RISKS/ASSUMPTIONS
	- Please note that there is maybe delay of delivery because of there is no knowledge about these new features
		in the testing team, so testing team will need some time for learning curve and manual tries for these features.
	- will use the new testing procedure which is running everything through cockpit and AYS which is not fully clear
		for the testing team yet.

