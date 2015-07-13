## Tests for OpenvCloud from an end user perspective
Mark failing tests with a :x: and passing tests with :white_check_mark:

## Prerequisites
* OpenvCloud environment and credentials to log in to the mountaintop portal

## 1. Machines
| #  | Result|Test | Comment  | Youtrack issue |
|----|-------|-----|----------|----------------|
|1.1 | :white_check_mark: |Create machine with a name and all other options left to default | | |
|1.2 | | Check if console works in the machine details and login is possible with the provided credentials | | |
|1.3 | | ping google.com | | |
|1.4 | | Create Ubuntu 14.04 vm with name test2 and 40 GB disk | | |
|1.5 | | Create a big file on the first vm `dd if=/dev/urandom of=test.file bs=1024 count=0 seek=$[1024*100]`| | |
|1.6 | | Log in to test2 and copy the file just created on the first vm: `scp cloudscalers@[ip.of.first.vm]:test.file .` | | |
|1.7 | | Check if the files are equal `md5 test.file` (compare output on both systems) | | |
|1.8 | | Create Windows vm with name test3 and 90 GB disk | | |
|1.9 | | Create portforward of public port 3389 to test3 port 3389 | | |
|1.10| | Use an rdp client to log in to test3 on the public ip with the provided credentials | | |
|1.11| | Create a new file named beforesnapshot.txt on the desktop | | |
|1.12| | Take a snapshot of test3 named "pristine" | | |
|1.13| | Log in again on test3 and create a new file aftersnapshot.txt on the desktop | | |
|1.14| | Roll back to the snapshot named "pristine" | | |
|1.15| | Log in again on test3 and check if beforesnapshot.txt is there but not aftersnapshot.txt | | |
|1.16| | Repeat test 1.13 - 1.15 | | |
