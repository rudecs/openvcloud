import whmcsusers

users = whmcsusers.list_users()
for user in users:
    whmcsusers.delete_user(users[user]['id'])
