'use strict';

angular.module('cloudscalers.services')
.factory('Users', function($http, $q) {
  return {
    updatePassword: function(username, oldPassword, newPassword) {
      var data = {username: username, oldPassword: oldPassword, newPassword: newPassword};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/updatePassword', data)
      .then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    sendResetPasswordLink: function(emailaddress) {
      var data = {emailaddress: emailaddress};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/sendResetPasswordLink', data)
      .then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    getResetPasswordInformation: function(resettoken) {
      var data = {resettoken: resettoken};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/getResetPasswordInformation', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    resetPassword: function(resettoken, newpassword) {
      var data = {resettoken: resettoken, newpassword: newpassword};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/resetPassword', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    activateUser: function(token, newpassword) {
      var data = {validationtoken: validationtoken, password: newpassword};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/validate')
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    tourTipsSwitch: function(tourtipsStatus) {
      return $http.post(cloudspaceconfig.apibaseurl + '/users/setData?' , {
        'data': {'tourtips': encodeURIComponent(tourtipsStatus)}
      }).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    // TODO make usernameregex dynamic
    getMatchingUsernames: function() {
      var data = {limit: 5, usernameregex: 'k'};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/getMatchingUsernames', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    isValidInviteUserToken: function(inviteUserToken, emailAddress) {
      var data = {inviteusertoken: inviteUserToken, emailaddress: emailAddress};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/isValidInviteUserToken', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    registerInvitedUser: function(inviteUserToken, emailAddress, userName, passWord, confirmPassword) {
      var data = {inviteusertoken: inviteUserToken, emailaddress: emailAddress, username: userName,
                  password: passWord, confirmpassword: confirmPassword};
      return $http.post(cloudspaceconfig.apibaseurl + '/users/registerInvitedUser', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
});
