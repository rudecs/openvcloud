## OpenvCloud API Functional Tests

There are currently two test suites for the OpenvCloud APIs:
- Access Control List API
- OpenvCloud API (covering all non-ACL APIs)

The actual tests are auto-documented [here](http://85.255.197.106:8888/) using **Sphinx**. For instructions on how to set-up this auto-documentation see the [section about auto-documentation](../../sphinx.md) in this guide.

In order to install and run the API test suites you have two options:
- [Install and run from a remote machine, using **run\_tests\_remote.sh**](#remote)
- [Install and run directly on **ovc_master**, using **setup\_run\_tests\_local.sh**](#local)

Both options are discussed here below.

<a id="remote"></a>
### Install and run from a remote machine

There are two steps:
1. Clone the **G8_testing** repository to the remote machine, probably your local machine
2. Run the **run\_tests\_remote.sh** script with the required parameters:
  - **[grid_name]** specifies the name of the grid
  - **[env_name]** specifies the name of the environment
  - **[test_suite]** specifies the test suite to execute, optionally indicating that you only want to run a specific vest case of the test suite, all formatted as:
    - **[python\_script\_name]**:**[class\_name]**.**[test\_case\_name]**
  - Use the **-b** option to specify the branch of the test suite

> **Note**: Make sure that your private SSH key is stored in the **.ssh** directory on the remote machine, since the **run\_tests\_remote.sh** script will look for it there, ignoring the private key that has been loaded in the memory of **ssh-agent**. So using the -A option when connecting over SSH to a remote machine where your SSH keys are not in the **.ssh** directory will result in **run\_tests\_remote.sh** not being able to get to access your private SSH key, and not being able to connect to GitHub.

So first, clone the **G8_testing** repository:
```
git clone git@github.com:0-complexity/G8_testing.git
```

Then go to the **Openvcloud** directory:
```
cd G8_testing/functional_testing/Openvcloud/
```

And finally execute the **run_tests_remote.sh** script with the required parameters, for instance:
```
bash tools/run_tests_remote.sh -b master be-g8-3 be-g8-3 ovc_master_hosted/ACL/a_basic_operations/acl_account_test.py:Read.test003_account_get_with_readonly_user
```

In the above example:
- **Branch**: "master"
- **Grid**: "be-g8-3"
- **Environment**: "be-g8-3"
- **Python script**: "ovc_master_hosted/ACL/a_basic_operations/acl_account_test.py"
- **Class**: "Read()"
- **Test case**: "test003\_account\_get\_with\_readonly\_user()"

What actually will happen:
- It will connect to **ovc\_master** where it will clone the **G8_testing** repository
  - As the script will lookup to SSH key from the environment repository, make sure that you have access to it
- It will call the **setup_run_tests_local.sh** which is discussed below passing the test case parameters
- The result will be fed back in the file **testresults.xml** and all collected log information in the **logs** directory


<a id="local"></a>
### Install and run directly on ovc_master

There are three steps:
1. Get access to **ovc\_master**
  - See the [How to Connect to an OpenvCloud Environment](https://gig.gitbooks.io/ovcdoc_public/content/Sysadmin/Connect/connect.html) documentation in the [OpenvCloud Operator's Guide](https://www.gitbook.com/book/gig/ovcdoc_public/details)
2. Clone the **G8_testing** repository on **ovc\_master** in the directory `/opt/code/github/0-complexity`:
3. Run the **setup\_run\_tests\_local.sh** script with the required pareameters:
  - [test_suite branch] specifies the branch of the test suite to be used
  - [local\_directory] speficies the directory on ovc_master where you want the specified branch be cloned
  - [env_name] specifies the name of the environment
  - [test_path] specifies the actual test to be used, this path is formatted as [full path of the Python script]:[Class of the test suite][test case]

So first, clone the **G8_testing** repository:
```
cd /opt/code/github/0-complexity
git clone git@github.com:0-complexity/G8_testing.git
```

Then go to the **Openvcloud** directory:
```
cd cd G8_testing/functional_testing/Openvcloud/
```

And finally execute the **setup\_run\_tests\_local.sh** script with the required parameters, for instance:
```
bash setup_run_tests_local.sh master /opt/code/github/0-complexity be-g8-3 ovc_master_hosted/ACL/a_basic_operations/acl_account_test.py:Read.test003_account_get_with_readonly_user
```

This will run the **test003\_account\_get\_with\_readonly\_user()** test case of the **Read()** class that is implemented in the **acl_account_test.py**, located in the directory **ovc\_master\_hosted/ACL/a\_basic\_operations/**.


### Test results

You might want to install and use **tidy** in order to nicely format **testresults.xml**:

```
apt-get install tidy
tidy -xml -i testresults.xml > output.xml
cat output.xml
<?xml version="1.0" encoding="utf-8"?>
<testsuite name="nosetests" tests="1" errors="0" failures="0" skip="0">
  <testcase classname="functional_testing.Openvcloud.ovc_master_hosted.ACL.a_basic_operations.acl_account_test.Read" name="test003_account_get_with_readonly_user" time="4.151">
  </testcase>
</testsuite>
```
