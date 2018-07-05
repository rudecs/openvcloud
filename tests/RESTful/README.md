## OpenvCloud RESTful api  Tests



### Continues Integration

### Travis
You can trigger the build from [Travis website](https://travis-ci.org/0-complexity/G8_testing) or [CI-Dashboard](https://travis-dash.gig.tech/).

#### Prerequisites
Travis CI build uses the environment's controller to execute the tests from it, so if your environment controller doesn't have public ip you have to:
- Install zerotier [ZeroTier](zerotier.com/network) on the controller.
- Create zerotier network and make the controller join it.

#### Travis Parameters
  - ```ctrl_ipaddress```: controller's ip address (zerotier ip in case your using zerotier).
  - ```ctrl_user```: controller's non-root user (default: gig)
  - ```ctrl_user_password```: controller user ssh password.
  - ```environment```: environment's location code.
  - ```restful_ip```: the ip of the api server
  - ```restful_port```: the port of the api server
  - ```username```: [itsyou.online](https://itsyou.online) username
  - ```client_id```: [itsyou.online](https://itsyou.online) client id
  - ```client_secret```: [itsyou.online](https://itsyou.online) client secret  

  - ```jobs```: jobs to be executed (for example ```ovc-restful``` to execute only ovc and restful jobs).
  - ```restful_testsuite_dir```: restful tests path.

  - ##### In case you are using zerotier
    - ```zerotier_network```: zerotier network id.
    - ```zerotier_token```: zerotier account token.

### LOCAL EXECUTION:
As long as your machine can ping the enviroment, You can execute this test suite from your local mcahine. You only need to update the `config.ini` file to be look like that
```
[main]
ip=be-g8-3.demo.greenitglobe.com
port=443
username=gig_qa_1@itsyouonline
client_id=********************************
client_secret=****************************
location=be-g8-3
```
then you can fire it using nosetests. 

#### Example
```bash
nosetests-3.4 -sv  --logging-level=WARNING --rednose  testcases/cloudapi/test01_disks.py --tc-file config.ini
```

#### Steps to add new test case:
To implement any test case in REST APIs test suite please, create a new task with the following pattern:

````yaml
TC name:
TC ID:
API:

SCENARIOS:
  1- PERMISSION scenario.
       Parameterize [permitted user do correct actions > success, 
                            permitted user do incorrect actions > fail,
                            non-permitted user do actions > fail]
  2- OPERATION scenarioS:
      You can create any number of test cases to be sure that it will cover almost all use cases of this API.

NOSETEST COMMAND:
   nosetest command to fire these test cases.
```

