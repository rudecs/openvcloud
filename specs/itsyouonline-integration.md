# ItsYouOnline Integration into OpenvCloud

## Purpose

Make it possible to login to an OpenvCloud environment by using ItsYouOnline as an Oauth2 provider.
This will make it easier to gain access to environment withouth recreating the same user over and over again.
This will also force all users to login with their OWN user no shared user, this makes auditing work as it is intended.

## Work required

Add an oauth client during instalation of openvcloud which point to an umbrella organization inside ItsYouOnline.
Within these organization we will create sub organizations which represents groups inside OpenvCloud.

During login the requested scope will be something like this.
```
user:memberof:greenitlobe.environments.du-conv-3.level1,
user:memberof:greenitlobe.environments.du-conv-3.level2,
user:memberof:greenitlobe.environments.du-conv-3.level3,
user:memberof:greenitlobe.environments.du-conv-3.admin,
user:memberof:greenitlobe.environments.du-conv-3.ovs_admin,
user:memberof:greenitlobe.environments.du-conv-3.user
```

After login the ItsYouOnline user will be synced/cached in the JumpScale model all groups and emails will be overriden from the existing request.
When removing or adding a user to an organization the user will be required to reloin to the OpenvCloud.


## Example organization structure on ItsYouOnline
```yaml
greenitglobe
  environments
    - du-conv-3
       admin
       level1
       level2
       level3
       ovs-admin
    - du-conv-2
       admin
       level1
       level2
       level3
       ovs-admin
```

These organization can have access to other organization. So we can give access per organization and per user.
