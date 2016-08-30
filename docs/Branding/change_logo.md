## Change the Logo in Cloud Broker and End User Portals

Can be accomplished by replacing four files on **ovc_master**.

For the Open vStorage Portal another three files need to be replaced on all CPU nodes.


### Login

On **ovc_master** replace the file `logo.png` in the directory:
`/opt/code/git/binary/openvcloud/apps/oauthserver/html`


### Cloud Broker Portals

On **ovc_master** replace the file `green.png` in following directories:
- `/opt/code/git/0-complexity/openvcloud/apps/cbportal/base/CBGrid/.files/`
- `/opt/code/github/jumpscale/jumpscale_portal/apps/portalbase/wiki/System/.files/img`


### End User Portal

On **ovc_master** replace the files `logo-colored.png` and `favicon.jpg` in the directory:
`/opt/code/git/0-complexity/openvcloud/apps/ms1_fe/base/wiki_gcb/.files/img/`


### Open vStorage

On each CPU node replace the files `noice.png`, `ovssmall.png` and `ovssplash.png` in the directory:
`/opt/OpenvStorage/webapps/frontend/lib/ovs/images/`
