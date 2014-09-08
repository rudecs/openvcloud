
from JumpScale import j
from JumpScale import grid

import whmcsusers











cb = j.core.osis.getClientForNamespace('cloudbroker')
system = j.core.osis.getClientForNamespace('system')



accounts = cb.account.list()
users = whmcsusers.list_users()
for user in users:
    whmcsusers.delete_user(users[user]['id'])
for i in accounts:
  acc = cb.account.get(i)
  linked_users = system.user.simpleSearch({'id':acc.name})
  if len(linked_users) != 1:
    continue
  linked_user = linked_users[0]
  linked_groups = system.group.simpleSearch({'id':acc.name})
  if len(linked_groups) != 1:
    continue
  print linked_user
  password = ''
  if 'passwd' in linked_user:
      password =linked_user['passwd']
  if not acc.name in users.keys():
      whmcsusers.create_user(acc.name, acc.company, linked_user['emails'], password, acc.companyurl, acc.displayname, acc.creationTime)
