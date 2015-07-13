## Extended tests for OpenvCloud from an end user perspective
Mark failing tests with a :x: and passing tests with :white_check_mark:


## 1. Platform
| #  | Result|Test | Comment  | Youtrack issue |
|----|-------|-----|----------|----------------|
|1.1 | :white_check_mark: |Log in to mountaintop by going to https://[env].demo.greenitglobe.com . Your browser should not give security warnings.| | |



## 2. Machines
| #  | Result|Test | Comment  | Youtrack issue |
|----|-------|-----|----------|----------------|
|2.1 | :white_check_mark: |Create machine with a name and all other options left to default | | |
|2.2 | | Check if console works in the machine details and login is possible with the provided credentials | | |
|2.3 | | ping google.com | | |
|2.4 | | Create Ubuntu 14.04 vm with name test2 and 40 GB disk | | |
|2.5 | | Create a big file on the first vm `dd if=/dev/urandom of=test.file bs=1024 count=0 seek=$[1024*100]` Log in to test2 and copy the file just created on the first vm: `scp cloudscalers@[ip.of.first.vm]:test.file .` Check if the files are equal `md5 test.file` (compare output on both systems) | | |
|2.6 | | Create Windows vm with name test3 and 90 GB disk | | |
|2.7 | | Create portforward of public port 3389 to test3 port 3389 | | |
|2.8 | | Use an rdp client to log in to test3 on the public ip with the provided credentials | | |
|2.9 | | Create a new file named beforesnapshot.txt on the desktop | | |
|2.10| | Take a snapshot of test3 named "pristine" | | |
|2.11| | Log in again on test3 and create a new file aftersnapshot.txt on the desktop. Roll back to the snapshot named "pristine". Log in again on test3 and check if beforesnapshot.txt is there but not aftersnapshot.txt | | |
|2.12| | Repeat test 2.11 | | |
|2.13| | Open the defense shield of the cloudspace | | |



## Other isses
File any other issues you noticed in this section

| # | Result | Description  | Youtrack issue |
|---|--------|--------------|----------------|
