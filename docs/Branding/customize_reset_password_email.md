## How to customize the body of the resend password e-mail

Get access to the ovc_master docker of your environment.

For detailed instructions on how to connect to ovc_master check the [How to Connect to an Environment](connect.md) documentation.

In summary:
- Clone the git repository to your personal computer, check the [Preparing for indirect access to ovc_git](preparing_for_indirect_access.md) documentation for this
- Connect to ovc_git:
  ```
  ssh $ip-address-of-master-cloud-space$ -l root -A -p 2202 -i /opt/code/git/openvcloudEnvironments/poc/keys/git_root
  ```
- On ovc_git lookup the ip address (instance.ip) of ovc_master in `service.hrd` of `/opt/code/git/openvcloudEnvironments/$name-of-your-env$/services/jumpscale__node.ssh__ovc_master`
- From ovc_git connect over ssh:
  ```
  ssh $ip-address-of-ovc_master$
  ```

On ovc_master the body text is under `/opt/jumpscale7/apps/portals/main/templates/cloudbroker/email/users`:

Simply change it and see the immediate effect:
```
vi reset_password.html

<html>
<head></head>
<body>
    Dear,<br>
    <br>
    A request for a password reset on the OpenvCloud service has been submitted using this email address.
    <br>
    <br>
    You can set a new password for the user {{ username }} using the following link: <a href="{{ portalurl }}/wiki_gcb/ResetPassword?token={{ resettoken }}">{{ portalurl }}/wiki_gcb/ResetPassword?token={{ resettoken }}</a>
    <br>
    If you are unable to follow the link, copy and paste it in your favorite browser.
    <br>
    <br>
    <br>
    In case you experience any issue logging in or using the OpenvCloud service, please contact us at support@greenitglobe.com
    <br>
    <br>
    <div>
        Best Regards,<br>
        <br>
        Your OpenvCloud Team<br>
    </div>
</body>
</html>root@ovc_master:/opt/jumpscale7/apps/portals/main/templates/cloudbroker/email/users#

```
