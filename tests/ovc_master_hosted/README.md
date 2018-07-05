## OpenvCloud Functional Tests Hosted on ovc_master

All OpenvCloud functional tests designed to run on ovc_master are documented [here](/docs/functional/openvcloud/ovc_master_hosted/ovc_master_hosted.md).

Below only **internal** documentation please.

## Continues Integration

### Travis
You can trigger the build from [Travis website](https://travis-ci.org/0-complexity/G8_testing) or [CI-Dashboard](https://travis-dash.gig.tech/).

#### Prerequisites
Travis CI build uses the environment's controller to execute the tests from it, so if your environment controller doesn't have public ip you have to:
- Install zerotier [ZeroTier](zerotier.com/network) on the controller.
- Create zerotier network and make the controller join it.

#### Jobs
OpenvCloud Travis build consists of 3 jobs running in parallel, each job executes one of the OpenvCloud's testsuites.
- ```ovc``` job: executes tests located in *functional_testing/Openvcloud/ovc_master_hosted/OVC*.
- ```acl``` job: executes tests located in *functional_testing/Openvcloud/ovc_master_hosted/ACL*.
- ```portal``` job: executes tests located in *functional_testing/Openvcloud/ovc_master_hosted/Portal*.

#### Travis Parameters
- ##### Environment
  - ```environment```: environment name (for example: **be-g8-3**).
  - ```ctrl_ipaddress```: controller's ip address (zerotier ip in case your using zerotier).
  - ```ctrl_root_user```: controller's root user (default: root).
  - ```ctrl_root_password```: controller root ssh password.
  - ```ctrl_user```: controller's non-root user (default: gig)
  - ```ctrl_user_password```: controller user ssh password.

- ##### Jobs
  - ```jobs```: jobs to be executed (for example ```acl-ovc``` to execute only ovc and acl jobs).
  - ```ovc_testsuite_dir```: ovc tests path.
  - ```acl_testsuite_dir```: acl tests path.
  - ```portal_testsuite_dir```: portal tests path.

    In case you want to run multiple files use  ```--tests=<PATH1> <PATH2>```.

    for example to run ovc extended and advanced tests
    ```
    ovc_testsuite_dir = --tests ovc_master_hosted/OVC/b_extended/,ovc_master_hosted/OVC/c_advanced/
    ```

- ##### In case you are using zerotier
  - ```zerotier_network```: zerotier network id.
  - ```zerotier_token```: zerotier account token.

- ##### Required for portal job
  - ```portal_admin```: [itsyou.online](itsyou.online) username.
  - ```portal_password```: [itsyou.online](itsyou.online) password.
  - ```portal_secret```: [itsyou.online](itsyou.online) otp secret.
  - ```portal_browser```: web browser to execute portal tests (default: chrome).

- ##### Other parameters
  - ```test_email```: test email to be used inside the tests.
  - ```test_email_password```: the password of the ```test_email```.


### Jenkins
OpenvCloud Testsuite runs continuously on [Jenkins CI](http://ci.codescalers.com/view/Integration%20Testing/)

## Instructions on how to update the coverage documentation

#### Prerequisites

* This instruction works for UNIX-Like operating systems
* Make sure that *pip* and *virtualenv* are installed to your system

    ```shell
    $ sudo apt-get install python-pip
    $ sudo pip install virtualenv
    ```


#### Steps to update

1. Pull the testsuite repository:

  ```
  git clone git@github.com:0-complexity/G8_testing.git
  ```

2. Change directory to Openvcloud:

  ```
  $ cd G8_testing/
  ```

3. Run the build script to generate the documentation locally:

  ```
  $ bash functional_testing/Openvcloud/tools/build_docs.sh
  ```

4. Open the documentation using any browser

  ```
  $ firefox auto_generated_docs/_build/html/index.html
  ```
