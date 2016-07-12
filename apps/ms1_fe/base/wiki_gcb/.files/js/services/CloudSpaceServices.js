'use strict';

angular.module('cloudscalers.services')
.factory('CloudSpace', function($http, $q, $window, SessionData) {
  return {
    list: function() {
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/list')
      .then(
        function(result) {
          return result.data;
        },function(reason) {
          return $q.reject(reason);
        });
    },
    current: function() {
      return SessionData.getSpace();
    },
    setCurrent: function(space) {
      SessionData.setSpace(space);
    },
    create: function(name, accountId, userId, location) {
      var data = {name: name, accountId: accountId, access: userId, location: location};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/create', data)
      .then(
        function(result) {
          if (result.status === 200) {
            return result.data;
          } else {
            return $q.reject(result);
          }
        }, function(reason) {
          return $q.reject(reason);
        }
      );
    },
    get: function(cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/get', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    getDefenseShield: function(cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/getDefenseShield', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    getOpenvpnConfig: function(cloudspaceId) {
      return $window.open(cloudspaceconfig.apibaseurl + '/cloudspaces/getOpenvpnConfig?cloudspaceId=' + cloudspaceId);
    },
    addUser: function(space, user, accessType) {
      var data = {cloudspaceId: cloudspaceId, accesstype: accessType, userId: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/addUser', data)
      .then(
        function(result) { return result.data;},
        function(reason) { return $q.reject(reason);
      });
    },
    inviteUser: function(space, user, accessType) {
      var data = {cloudspaceId: space.id, accesstype: accessType, emailaddress: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/addExternalUser', data)
      .then(
        function(result) { return result.data;},
        function(reason) { return $q.reject(reason);
      });
    },
    deleteUser: function(space, userId) {
      var data = {cloudspaceId: space.id, userId: userId};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/deleteUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason);
      });
    },
    delete: function(cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/delete', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason); }
      );
    },
    cloudspaceAccessRights: function() {
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
    },
    updateUser: function(cloudspaceId, userId, accesstype) {
      var data = {cloudspaceId: cloudspaceId, userId: userId, accesstype: accesstype};
      return $http.post(cloudspaceconfig.apibaseurl + '/cloudspaces/updateUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason);
      });
    },
    searchAcl: function(query) {
      var data = {limit: 5, usernameregex: query};
      var url = cloudspaceconfig.apibaseurl + '/users/getMatchingUsernames';
      return $http.post(url, data).then(
        function(response) {
          return response.data;
        }, function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
});

