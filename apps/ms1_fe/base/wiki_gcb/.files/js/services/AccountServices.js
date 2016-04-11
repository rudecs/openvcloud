'use strict';
angular.module('cloudscalers.services')
.factory('Account', function($http, $q, SessionData) {
  return {
    list: function() {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/list').then(
        function(result) {
          return result.data;
        });
    },
    listUsers: function() {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/listUsers').then(
        function(result) {
          return result.data;
        });
    },
    current: function() {
      return SessionData.getAccount();
    },
    setCurrent: function(account) {
      SessionData.setAccount(account);
    },

    get: function(id) {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/get?accountId=' + id).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    addUser: function(accountId, user, accessType) {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/addUser?accountId=' +
      accountId + '&accesstype=' + accessType + '&userId=' + user)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);
      });
    },
    inviteUser: function(accountId, user, accessType) {
      return $http
        .get(cloudspaceconfig.apibaseurl + '/accounts/addExternalUser?accountId=' +
        accountId + '&accesstype=' + accessType + '&emailaddress=' + user)
        .then(function(result) {
          return result.data;
        }, function(reason) {
          return $q.reject(reason);
        });
    },
    updateUser: function(accountId, userId, accesstype) {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/updateUser?accountId=' + accountId +
      '&userId=' + userId + '&accesstype=' + accesstype)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason);
      });
    },
    deleteUser: function(accountId, userId) {
      return $http.get(cloudspaceconfig.apibaseurl +
      '/accounts/deleteUser?accountId=' + accountId + '&userId=' + userId)
      .then(function(result) { return result.data; },
        function(reason) { return reason.data;
      });
    },
    getCreditBalance: function(account) {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/getCreditBalance?accountId=' + account.id)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);}
      );
    },
    getCreditHistory: function(account) {
      return $http.get(cloudspaceconfig.apibaseurl + '/accounts/getCreditHistory?accountId=' + account.id)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);}
      );
    },
    getUsage: function(account, reference) {
      return $http.get(cloudspaceconfig.apibaseurl + '/consumption/get?accountId=' + account.id +
      '&reference=' + encodeURIComponent(reference))
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason); }
      );
    },
    accountAccessRights: function() {
      var accessRights = [
        {
          name: 'Read',
          value: 'R'
        },
        {
          name: 'Read/Write',
          value: 'CRX'
        },
        {
          name: 'Admin',
          value: 'ACDRUX'
        }];
      return accessRights;
    }
  };
});
