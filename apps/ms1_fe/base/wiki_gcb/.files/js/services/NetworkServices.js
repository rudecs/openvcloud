'use strict';

angular.module('cloudscalers.services')
.factory('Networks', function($http, $q) {
  return {
    listPortforwarding: function(id, machineId) {
      var data = {};
      if (encodeURIComponent(id) !== 'undefined') {
         data['cloudspaceId'] = id;

      }
      if (machineId) {
        data['machineId'] = machineId;
      }
      return $http.post(cloudspaceconfig.apibaseurl + '/portforwarding/list', data)
      .then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    createPortforward: function(id, ip, publicPort, machineId, localPort, protocol) {
      var data = {cloudspaceId: id, publicIp: ip, publicPort: publicPort, machineId: machineId,
                  localPort: localPort, protocol: protocol};
      return $http.post(cloudspaceconfig.apibaseurl + '/portforwarding/create', data)
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
      var data = {cloudspaceId: cloudspaceId, publicIp: ip, publicPort: publicPort, id: id,
                  machineId: machineId, localPort: localPort, protocol: protocol};
      return $http.post(cloudspaceconfig.apibaseurl + '/portforwarding/update', data)
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
      var data = {cloudspaceId: cloudspaceId, publicIp: publicIp, publicPort: publicPort};
      return $http.post(cloudspaceconfig.apibaseurl + '/portforwarding/deleteByPort', data)
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
