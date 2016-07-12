'use strict';
angular.module('cloudscalers.services')
.factory('Account', function($http, $q, SessionData) {
  return {
    list: function() {
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/list').then(
        function(result) {
          return result.data;
        });
    },
    listUsers: function() {
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/listUsers').then(
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
      var data = {accountId: id};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/get', data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    addUser: function(accountId, user, accessType) {
      var data = {accountId: accountId, accesstype: accessType, userId: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/addUser', data)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);
      });
    },
    inviteUser: function(accountId, user, accessType) {
      var data = {accountId: accountId, accesstype: accessType, emailaddress: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/addExternalUser', data)
        .then(function(result) {
          return result.data;
        }, function(reason) {
          return $q.reject(reason);
        });
    },
    updateUser: function(accountId, userId, accesstype) {
      var data = {accountId: accountId, accesstype: accesstype, userId: userId};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/updateUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason);
      });
    },
    deleteUser: function(accountId, userId) {
      var data = {accountId: accountId, userId: userId};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/deleteUser', data)
      .then(function(result) { return result.data; },
        function(reason) { return reason.data;
      });
    },
    getCreditBalance: function(account) {
      var data = {accountId: account.id};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/getCreditBalance', data)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);}
      );
    },
    getCreditHistory: function(account) {
      var data = {accountId: account.id};
      return $http.post(cloudspaceconfig.apibaseurl + '/accounts/getCreditHistory', data)
      .then(
        function(result) {return result.data;},
        function(reason) {return $q.reject(reason);}
      );
    },
    getUsage: function(account, reference) {
      var data = {accountId: account.id, reference: reference};
      return $http.post(cloudspaceconfig.apibaseurl + '/consumption/get', data)
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
