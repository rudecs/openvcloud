# Configuration File Details

The configuration file is needed by the [installer script](#installer-script.md) to setup the OpenvCloud system.

An example `system-config.yaml` file can be found [here](../scripts/kubernetes/config/system-config.yaml).

For example the `ssh` key in the config is used to specify the key needed for authorization on each node in the cluster. This same info is used to add the key to the authorized keys on the machine.

## Support

This section is used by the Teleport application to configure the access to the application.

To access the Teleport application you need to have a github oauth application which is defined in the `github` section as follows:

```yaml
support:
  github:
    client_id: 3216584165816f5v
    client_secret: 3wa651wvefqeffefefsf6514651eswrfgw
    teams:
    - team_name: support_beg84
      org_name: be-g8-4
```

To create a GitHub OAuth application follow the [Creating an OAuth App](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/) documentation.

After creating the application you can get both the `client_id` and the `client_secret` from the application page.

Under the `teams` section it is possible to restrict the access to users belonging to a specific GitHub organization as well as specify a specific team that belongs to this organization.

## Validation 

@TODO