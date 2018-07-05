from framework.api import utils

class Users:
    def __init__(self, api_client):
        self._api = api_client

    def get(self, username, password):
        return self._api.cloudapi.users.get(username=username)
        
    def authenticate(self, username, password):
        return self._api.cloudapi.users.authenticate(username=username, password=password)

    def getMatchingUsernames(self, usernameregex, limit):
        return self._api.cloudapi.users.getMatchingUsernames(usernameregex=usernameregex, limit=limit)
    
    def getResetPasswordInformation(self, resettoken):
        return self._api.cloudapi.users.getResetPasswordInformation(resettoken=resettoken)

    def isValidInviteUserToken(self, inviteusertoken, emailaddress):
        return self._api.cloudapi.users.authenticate(inviteusertoken=inviteusertoken, emailaddress=emailaddress)

    def registerInvitedUser(self, inviteusertoken, emailaddress, username, password, confirmpassword):
        return self._api.cloudapi.users.registerInvitedUser(
            inviteusertoken=inviteusertoken, 
            emailaddress=emailaddress,
            username=username,
            password=password,
            confirmpassword=confirmpassword
        )

    def resetPassword(self, resettoken, newpassword):
        return self._api.cloudapi.users.resetPassword(resettoken=resettoken, newpassword=newpassword)

    def sendResetPasswordLink(self, emailaddress):
        return self._api.cloudapi.users.sendResetPasswordLink(emailaddress=emailaddress)

    def setData(self, data):
        return self._api.cloudapi.users.setData(data=data)

    def updatePassword(self, data):
        return self._api.cloudapi.users.updatePassword(oldPassword=oldPassword, newPassword=newPassword)

    def validate(self, validationtoken, password):
        return self._api.cloudapi.users.validate(validationtoken=validationtoken, password=password)

    
