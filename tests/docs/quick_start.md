## How to execute Tests ?

```
sudo -i 
git clone https://github.com/0-complexity/openvcloud
cd openvcloud/tests
bash prepare.sh
```

### OVC & ACL Test

```
sudo -i
export PYTHONPATH=/opt/jumpscale7/lib:/opt/jumpscale7/lib/lib-dynload/:/opt/jumpscale7/bin:/opt/jumpscale7/lib/python.zip:/opt/jumpscale7/lib/plat-x86_64-linux-gnu
cd openvcloud/tests
```

set your configurations in the config.ini file as follow:

```environment```: Location name (from Cloudbroker > Locations)

```protocol```: http or https

##### Required for users tests

```email```: your testing email address

```email_password```: your testing email password

##### Required for export/import machine tests

```owncloud_user```: owncloud server username

```owncloud_password```: owncloud server password

```owncloud_url```: owncloud server url

```
nosetests-2.7 -s -v ovc_master_hosted/<testcase_path> --tc-file config.ini
```

### Portal Tests

```
cd openvcloud/tests/ovc_master_hosted/Portal
export PYTHONPATH=./
```

set your configurations in the config.ini file as follow:

```env```: Environment url (for example ```https://be-g8-3.demo.greenitglobe.com```)

```location```: Location name (Cloudbroker > Locations)

```admin```: itsyouonline account username

```passwd```: itsyouonline account password

```secret```: itsyouonline account totp secret (from Settings > View existing QR code)

```browser```: web browser to be used during tests

#### Normal mode
```
nosetests-3.4 -s -v testcases/admin_portal/ --tc-file config.ini
```

#### Headless mode
```
xvfb-run -a nosetests-3.4 -s -v testcases/admin_portal/ --tc-file config.ini
```
