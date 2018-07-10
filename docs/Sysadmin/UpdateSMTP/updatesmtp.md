# How to update email/smtp information

First of all you always need to make sure the git repo of the project is always your primary source and updated.

Once this is accomplished connect to the management pod via zero-access. Download your new system-config.yaml and update t
he pod config.

`installer --config mydownloadedconfig.yaml resources writeconfig`

After this we need to restart the portal pod to make our changes affective.

Connect to one of the 3 controllers via zero-access

`kubectl delete pod -l app=portal`
