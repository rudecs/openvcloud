## Errors

- **Errors during the bootstrap script**:
If any error occurs during the bootstrap, just re-run the script. It will restart where it left.  

```
HTTP Error 400: Bad Request
Traceback (most recent call last):
~   File "bootstrap.py", line 134, in <module>
    action(args.url)
~   File "bootstrap.py", line 89, in action
    pcl.actors.cloudapi.portforwarding.create(cloudspace['id'], cloudspace['publicipaddress'], publicport, vmachineId, 22, 'tcp')
~   File "/opt/jumpscale7/var/code/actorremote_cloudapi_actor_portforwarding_.py", line 45, in create
    resultcode,result=self._appserverclient.wsclient.callWebService("cloudapi","portforwarding","create",cloudspaceid=cloudspaceid,publicIp=publicIp,publicPort=publicPort,vmid=vmid,localPort=localPort,protocol=protocol)
~   File "/opt/jumpscale7/lib/JumpScale/portal/portal/PortalClientWS.py", line 73, in callWebService
    result = self.httpconnection.post(url, headers=headers, data=data)
~   File "/opt/jumpscale7/lib/JumpScale/baselib/http_client/HttpClient.py", line 87, in post
    response = self._http_request(url, data=data, headers=headers, method='POST',**params)
~   File "/opt/jumpscale7/lib/JumpScale/baselib/http_client/HttpClient.py", line 172, in _http_request
    raise HTTPError(e, url)
~ HTTPError: 400:
 "Invalid public IP "

type/level: UNKNOWN/1
<class 'JumpScale.baselib.http_client.HttpClient.HTTPError'>: 400:
 "Invalid public IP "
```

- **Errors during the setup script**:
It can happen that for some reason during the creation of the virtual machines, the scripts time out or an error happens. To restart don't re-run the script itself but just do:
```
cd /opt/code/git/0-complexity/ays_stresstest; ays apply
```

This will restart AYS and continue the deployment of the virtual machines.

- If you get this error message during deployment of the virtual machines, just press ```enter```
```
┌────────────────────────────────────────────────────────┤  ├────────────────────────────────────────────────────────┐
│ A new version of /boot/grub/menu.lst is available, but the version installed currently has been locally modified.  │
│                                                                                                                    │
│ What would you like to do about menu.lst?                                                                          │
│                                                                                                                    │
│                             install the package maintainer's version                                               │
│                             keep the local version currently installed                                             │
│                             show the differences between the versions                                              │
│                             show a side-by-side difference between the versions                                    │
│                             show a 3-way difference between available versions                                     │
│                             do a 3-way merge between available versions (experimental)                             │
│                             start a new shell to examine the situation                                             │
│                                                                                                                    │
│                                                                                                                    │
│                                                       <Ok>                                                         │
│                                                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **During git clone, your password is asked for github.com or git.aydo.com**:
This means you did not have your ssh keys loaded in ssh-agent or ssh-agent is not running at all.
Make sure to have ssh-agent running when connecting to the master virtual machine and using ```-A``` option in you ssh command.
```
ssh root@vmip -A
```
