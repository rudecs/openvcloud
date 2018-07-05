# OpenvCloud Portals Functional Tests
## 1. Introduction:
The goal of the portal test suit is testing the OpenvCloud portals. There are currently two sets of functional test suites for the OpenvCloud portals:

- One covering the **End User Portal**
- Another is covering the **Cloud Broker Portal**

The portal testing framework has been building depending on selenium framework to automate different browsers on different OS.

The documentation for these functional tests is embedded in the actual test code. For instructions on how to setup an **Read the Docs** site consolidating the embedded documentation see the section [Setup a Read the Docs site for your Testing Suite](../../sphinx.md) in this guide.

## 2. Portal Test Suit Architecture:
```
Portal
  | framework # This directory includes the implementation of the testing framework.
  | testcases # This directory includes the implementation of the test cases.
    | admin_portal # This directory includes the test cases which cover **Cloud Broker Portal**.
    | end_user # This directory includes the test cases which cover **End User Portal**.
  | config.ini # This configuration file includes the configuration parameters.
  | requirements.txt # This file include all the requirement python packages.
  | run_portal_tests.sh # This file includes the bash script to automatically execute the test suit.
```
## 3. Grid concept:
- The test suite can be executed either on a single machine or Grid (multiple machines)

### 3.1 What is a grid?:
- A Grid allows you to run your tests on different machines against different browsers. That is, running multiple tests at the same time against different machines running different browsers and operating systems. It allows for running your tests in a distributed test execution environment.

- In grid execution, Tester is using a selenium server as hub, chrome node, firefox node and any other browser node. In this documentation, we will introduce how to prepare a testing environment which has hub, chrome node and firefox node as a docker containers. (Note: you can design your own grid as needed)

### 3.2 Prepare The Grid:
After installing the docker service in any machine operating system, run the following commands:
```
docker run -d -p 4444:4444 --name selenium-hub selenium/hub
docker run -d --name chrome-node --link selenium-hub:hub selenium/node-chrome
docker run -d --name firefox-node --link selenium-hub:hub selenium/node-firefox
```
- Now If you are running your tests from the machine which contains the dockers, you can access your selenium-hub which is your remote server via **http://localhost:4444** and you can execute test cases on firefox-node and chrome-node.
- However if you want to connect to the selenium-hub (remote-webdriver) from your local machine (your own pc), You have to do a port forward from the cloudspace to the seleinum-hub and in which the remote webdriver will be **http://< cloudspace_ip>:4444** (Note: In this case the cloudspace_ip should be reachable from your local machine)


## 4. Test Suite Execution:
This test suite can be executed from Ubuntu Desktop or Server operating systems. There are two modes of execution:
- Automated execution
- Manual execution

### 4.1 Automated Execution:
In the automated execution mode, The tester will execute the portal test suite either on a single machine or on a grid.
#### 4.1.1 Single Machine Execution Guide:
- The tests should be executed from inside this single machine.

- After making sure your SSH private key is loaded by ssh-agent, clone the **G8_testing** repository:

  ```
  ssh-add -l
  git clone git@github.com:0-complexity/G8_testing.git
  ```

- Run the following command after replacing each <variable> with its value:

  ```
  cd G8_testing/
  sudo bash functional_testing/Openvcloud/ovc_master_hosted/Portal/run_portal_tests.sh -u <browser> -i <username> -p <password> -s <secret> -d <testcases directory> <environment_url> <location>
  ```
   - Browser : firefox or chrome
   - username : itsyou.online username
   - password : itsyou.online password
   - secret : itsyou.online secret key
   - testcase_directory : the directory of the test cases
   - environment_url : the environment url
   - location : the environment location
   Example:
   ```
  sudo bash functional_testing/Openvcloud/ovc_master_hosted/Portal/run_portal_tests.sh -u chrome -i username -p username123 -s BMDHEDMMGFZG7RBMDHEDMMGFZG7R -d testcases/admin_portal/cloud_broker/test01_accounts.py http://du-conv-2.demo.greenitglobe.com du-conv-2
   ```

The run_portal_tests.sh script will update the operating systems and install python, pip, virtualenv and all requirement package in requirement.txt. Then it will start a virtual environment. Then it will install chrome and firefox and finally execute the test cases in headless mode. Note: This script will not install firefox and chrome in case of grid execution as it expects that there are firefox and chrome installed on other machines.

#### 4.1.2 Grid Execution Guide:

- After making sure your SSH private key is loaded by ssh-agent, clone the **G8_testing** repository:

  ```
  ssh-add -l
  git clone git@github.com:0-complexity/G8_testing.git
  ```

- Run the following command after replacing each <variable> with its value:

  ```
  cd G8_testing/
  sudo bash functional_testing/Openvcloud/ovc_master_hosted/Portal/run_portal_tests.sh -r <remote_webdriver> -u <browser> -i <username> -p <password> -s <secret> -d <testcases directory> <environment_url> <location>
  ```
   - remote_webdriver : remote server ip:port
   - Browser : firefox or chrome
   - username : itsyou.online username
   - password : itsyou.online password
   - secret : itsyou.online secret key
   - testcase_directory : the directory of the test cases
   - environment_url : the environment url
   - location : the environment location
   Example:
   ```
  sudo bash functional_testing/Openvcloud/ovc_master_hosted/Portal/run_portal_tests.sh -r http://localhost:4444 -u chrome -i username -p username123 -s BMDHEDMMGFZG7RBMDHEDMMGFZG7R -d testcases/admin_portal/cloud_broker/test01_accounts.py http://du-conv-2.demo.greenitglobe.com du-conv-2
   ```

In the Grid execution, The run_portal_tests.sh script will only update the operating systems and install python, pip, virtualenv and all requirement package in requirement.txt then it will execute the test cases through the remote server.


### 4.2 Manual Execution:
In manual execution, Tester will install all dependencies and run the execution command manually on his machine. As for the automated execution, The Manual execution can be excuted on a single machine or on a grid.

#### 4.2.1 Execution Guide:
- The coming steps in this section are the same for single machine and grid execution.

- Prepare The Machine:

```
echo -e "${GREEN}** Installing xvfb ...${NC}"
sudo apt-get update
sudo apt-get install -y python-pip
sudo apt-get install -y xvfb
sudo apt-get install git

```

- After making sure your SSH private key is loaded by ssh-agent, clone the **G8_testing** repository:

```
  ssh-add -l
  git clone git@github.com:0-complexity/G8_testing.git
```

- To install the requirements, run:

```
cd G8_testing/functional_testing/Openvcloud/ovc_master_hosted/Portal
pip install -r requirements.txt
```

- Change the necessary parameters in **config.ini** according to your environment:

```
  [main]
  env = <environment_url>
  location = <locations>
  #location for the environment in the grid, ex.: du-conv-2,du-conv-1,du-conv-3
  admin = <username>
  passwd = <password>
  browser = <browser>
  secret = <secret>
  remote_webdriver = <remote_webdriver>
```
   - Browser : firefox or chrome
   - username : itsyou.online username
   - password : itsyou.online password
   - secret : itsyou.online secret key
   - environment_url : the environment url
   - location : the environment location
   - remote_webdriver : remote server ip:port (will be left empty in case of single machine execution)

  ##### 4.2.1.1 Single Machine Execution:
- The coming steps need to be added in case of single machine execution
- To execute this test suit, the machine should has chrome and firefox, so run the following commands to install them in the right way.

    ```
    echo -e "${GREEN}** Installing chromium ...${NC}"
    sudo apt-get install -y chromium-chromedriver
    sudo ln -fs /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
    sudo ln -fs /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver

    echo -e "${GREEN}** Installing firefox ...${NC}"
    sudo apt-get install -y firefox
    which geckodriver || (wget https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz; tar -C /opt -xzf /tmp/geckodriver.tar.gz;	chmod 755 /opt/geckodriver;	ln -fs /opt/geckodriver /usr/bin/geckodriver)

    ```
- Then if the machine has a Desktop OS, you run the following command:
  ```
  nosetests -v -s  --logging-level=WARNING <testsuite_directory> --tc-file=config.ini  2>testresults.log
  ```
Note: if you don't want to visualize the browser during running the tests, you can put "xvfb-run -a" before the previous command

- Otherwise if the machine has a server OS, use the following command instead:
   ```
   xvfb-run -a nosetests -v -s  --logging-level=WARNING <testsuite_directory> --tc-file=config.ini  2>testresults.log
   ```


  ##### 4.2.1.2 Grid Execution:
  - Make sure to provide value for the remote_webdriver parameter in the **config.ini** file
  - Assuming you already have a ready grid as explained before, run the following command using **nosetests**:
   ```
   xvfb-run -a nosetests -v -s  --logging-level=WARNING <testsuite_directory> --tc-file=config.ini  2>testresults.log
   ```


You can also overwrite the **config.ini** parameters:

```
nosetests -v testsuite --tc-file=config.ini --tc=main.url:http://be-conv-2.demo.greenitglobe.com/  --tc=main.admin:gig 2>testresults.log
```


## 5. Appendix:
### 5.1 How to get itsyouonline secret?
- During registering a new itsyou.online account, scan the QR code using any QR scanner or you can use **right-click QRcode reader** it is a free **google chrome extension**, and you will find the secret code after secret parameter in the message.
