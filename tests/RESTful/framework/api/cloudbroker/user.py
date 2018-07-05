import random
from framework.api import utils

class User:
    def __init__(self, api_client):
        self._api = api_client

    def create(self,**kwargs):
        data = {
            "username": utils.random_string(),
            "emailaddress": "%s@text.com" % utils.random_string(),
            "password": utils.random_string(),
            "groups": ["level1","user","level2","level3","admin"]
        }
        data.update(**kwargs)
        return data, self._api.cloudbroker.user.create(**data)

    def delete(self, username):
        return self._api.cloudbroker.user.delete(username=username)

    def deleteByGuid(self, userguid):
        return self._api.cloudbroker.user.deleteByGuid(userguid=userguid)
    
    def deleteUsers(self, userIds):
        return self._api.cloudbroker.user.deleteUsers(userIds=userIds)
    
    def generateAuthorizationKey(self, username):
        return self._api.cloudbroker.user.generateAuthorizationKey(username=username)
    
    def sendResetPasswordLink(self,username):
        return self._api.cloudbroker.user.sendResetPasswordLink(username=username)        

    def updatePassword(self, username, password):
        return self._api.cloudbroker.user.updatePassword(username=username, password=password)
