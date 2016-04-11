'use strict';

angular.module('cloudscalers.services')
.factory('Networks', function($http, $q) {
  return {
    listPortforwarding: function(id, machineId) {
      if (encodeURIComponent(id) === 'undefined') {
        return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list')
        .then(
          function(result) {
            return result.data;
          },
          function(reason) {
            return $q.reject(reason);
          }
        );
      }else {
        if (machineId) {
          return $http.get(cloudspaceconfig.apibaseurl +
            '/portforwarding/list?cloudspaceId=' + encodeURIComponent(id) +
            '&machineId=' + encodeURIComponent(machineId))
          .then(
            function(result) {
              return result.data;
            },function(reason) {
              return $q.reject(reason);
            }
          );
        } else {
          return $http.get(cloudspaceconfig.apibaseurl +
            '/portforwarding/list?cloudspaceId=' + encodeURIComponent(id))
          .then(
            function(result) {
              return result.data;
            },
            function(reason) {
              return $q.reject(reason);
            }
          );
        }
      }
    },
    createPortforward: function(id, ip, publicPort, machineId, localPort, protocol) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/portforwarding/create?cloudspaceId=' + encodeURIComponent(id) +
        '&publicIp=' + encodeURIComponent(ip) +
        '&publicPort=' + encodeURIComponent(publicPort) +
        '&machineId=' + encodeURIComponent(machineId) +
        '&localPort=' + encodeURIComponent(localPort) +
        '&protocol=' + encodeURIComponent(protocol))
      .then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    updatePortforward: function(cloudspaceId, id, ip, publicPort, machineId, localPort, protocol) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/portforwarding/update?cloudspaceId=' + encodeURIComponent(cloudspaceId) +
        '&id=' + encodeURIComponent(id) +
        '&publicIp=' + encodeURIComponent(ip) +
        '&publicPort=' + encodeURIComponent(publicPort) +
        '&machineId=' + encodeURIComponent(machineId) +
        '&localPort=' + encodeURIComponent(localPort) +
        '&protocol=' + encodeURIComponent(protocol))
      .then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    deletePortforward: function(cloudspaceId, publicIp, publicPort) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/portforwarding/deleteByPort?cloudspaceId=' + encodeURIComponent(cloudspaceId) +
        '&publicIp=' + encodeURIComponent(publicIp) +
        '&publicPort=' + encodeURIComponent(publicPort))
      .then(
        function(result) {
          return result;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    commonports: function() {
      return [
        {port: '80', name: 'HTTP'},
        {port: '443', name: 'HTTPS'},
        {port: '21', name: 'FTP'},
        {port: '22', name: 'SSH'},
        {port: '3389', name: 'RDP'}
      ];
    }
  };
});
