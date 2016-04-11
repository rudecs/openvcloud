'use strict';

angular.module('cloudscalers.services')
.factory('Users', function($http, $q) {
  return {
    updatePassword: function(username, oldPassword, newPassword) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/users/updatePassword?username=' + encodeURIComponent(username) +
        '&oldPassword=' + encodeURIComponent(oldPassword) +
        '&newPassword=' + encodeURIComponent(newPassword))
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
      return $http.get(cloudspaceconfig.apibaseurl +
        '/users/sendResetPasswordLink?emailaddress=' + encodeURIComponent(emailaddress)
      ).then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    getResetPasswordInformation: function(resettoken) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/users/getResetPasswordInformation?resettoken=' + encodeURIComponent(resettoken)
      ).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    resetPassword: function(resettoken, newpassword) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/users/resetPassword?resettoken=' + encodeURIComponent(resettoken) +
        '&newpassword=' + encodeURIComponent(newpassword)
      ).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    activateUser: function(token, newpassword) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/users/validate?validationtoken=' + encodeURIComponent(token) +
        '&password=' + encodeURIComponent(newpassword))
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
      return $http.get(cloudspaceconfig.apibaseurl + '/users/getMatchingUsernames?imit=5&usernameregex=k')
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
      return $http.get(cloudspaceconfig.apibaseurl +
      '/users/isValidInviteUserToken?inviteusertoken=' + encodeURIComponent(inviteUserToken) +
      '&emailaddress=' + encodeURIComponent(emailAddress))
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
      return $http.post(cloudspaceconfig.apibaseurl + '/users/registerInvitedUser?inviteusertoken=' +
      encodeURIComponent(inviteUserToken) + '&emailaddress=' + encodeURIComponent(emailAddress) +
      '&username=' + encodeURIComponent(userName) + '&password=' +
      encodeURIComponent(passWord) + '&confirmpassword=' + encodeURIComponent(confirmPassword))
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
