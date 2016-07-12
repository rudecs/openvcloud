'use strict';

angular.module('cloudscalers.services')
.factory('Machine', function($http, $q) {
  $http.defaults.get = {'Content-Type': 'application/json', 'Accept': 'Content-Type: application/json'};
  var machineStates = {
    'start': 'RUNNING',
    'stop': 'HALTED',
    'pause': 'PAUSED',
    'resume': 'RUNNING'
  };
  return {
    start: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/start';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['start'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    stop: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/stop';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['stop'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    reboot: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/reboot';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['start'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    reset: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/reset';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['start'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    pause: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/pause';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['pause'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    resume: function(machine) {
      var data = {machineId: machine.id};
      var url = cloudspaceconfig.apibaseurl + '/machines/resume';
      return $http.post(url, data).then(
        function(result) {
          machine.status = machineStates['resume'];
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    create: function(cloudspaceId, name, description, sizeId, imageId, disksize, archive, region, replication) {
      var data = {cloudspaceId: cloudspaceId, name: name, description: description, sizeId: sizeId,
                  imageId: imageId, disksize: disksize, archive: archive, region: region, replication: replication};
      var url = cloudspaceconfig.apibaseurl + '/machines/create';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    updateDescription: function(id, newdescription) {
      var data = {machineId: id, description: newdescription};
      var url = cloudspaceconfig.apibaseurl + '/machines/update';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    clone: function(machine, cloneName) {
      var data = {machineId: machine.id, name: cloneName};
      var url = cloudspaceconfig.apibaseurl + '/machines/clone';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        });
    },
    createTemplate: function(machine, templatename) {
      var data = {machineId: machine.id, templatename: templatename};
      var url = cloudspaceconfig.apibaseurl + '/machines/createTemplate';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    delete: function(machineid) {
      var data = {machineId: machineid};
      var url = cloudspaceconfig.apibaseurl + '/machines/delete';
      return $http.post(url, data).then(
        function() {
          return;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    list: function(cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId, type: ''};
      var url = cloudspaceconfig.apibaseurl + '/machines/list';
      return $http.post(url, data).then(function(result) {
        _.each(result.data, function(machine) {
          if (machine.status === 'SUSPENDED') {
            machine.status = 'PAUSED';
          }
        });
        return result.data;
      }, function(reason) {
        return $q.reject(reason);
      });
    },
    get: function(machineid) {
      var machine = {
        id: machineid
      };
      var data = {machineId: machineid};
      var url = cloudspaceconfig.apibaseurl + '/machines/get';
      return $http.post(url, data).then(
        function(result) {
          if (result.data.status === 'SUSPENDED') {
            result.data.status = 'PAUSED';
            _.each(result.data.acl, function(acl, i) {
              if (acl.right.indexOf('U') > -1 && acl.right.indexOf('U') > -1) {
                result.data.acl[i].right = 'ACDRUX';
              }
            });
          }
          return _.extend(machine, result.data);
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    listSnapshots: function(machineid) {
      var data = {machineId: machineid};
      var url = cloudspaceconfig.apibaseurl + '/machines/listSnapshots';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    createSnapshot: function(machineId, name) {
      var data = {machineId: machineId, name: name};
      var url = cloudspaceconfig.apibaseurl + '/machines/snapshot';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    rollbackSnapshot: function(machineId, epoch) {
      var data = {machineId: machineId, epoch: epoch};
      var url = cloudspaceconfig.apibaseurl + '/machines/rollbackSnapshot';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    deleteSnapshot: function(machineId, epoch) {
      var data = {machineId: machineId, epoch: epoch};
      var url = cloudspaceconfig.apibaseurl + '/machines/deleteSnapshot';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    getConsoleUrl: function(machineId) {
      var getConsoleUrlResult = {};
      var data = {machineId: machineId};
      var url = cloudspaceconfig.apibaseurl + '/machines/getConsoleUrl';
      $http.post(url, data).success(function(data, status) {
        if (data === 'None') {
          getConsoleUrlResult.error = status;
        } else {
          getConsoleUrlResult.url = JSON.parse(data);
        }
      }).error(function(data, status) {
        getConsoleUrlResult.error = status;
      });
      return getConsoleUrlResult;
    },
    getHistory: function(machineId) {
      var data = {machineId: machineId, size: 100};
      var url = cloudspaceconfig.apibaseurl + '/machines/getHistory';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },function(reason) {
          return $q.reject(reason);
        }
      );
    },
    deleteTemplate: function(templateIndex) {
      var data = {templateIndex: templateIndex}
      return $http.post(cloudspaceconfig.apibaseurl + '/template/delete?templateIndex=' + templateIndex)
      .then(
        function(result) {
          return result.data;
        },function(reason) {
          return $q.reject(reason);
        }
      );
    },
    addUser: function(machineId, user, accessType) {
      var data = {machineId: machineId, accesstype: accessType, userId: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/machines/addUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason); }
      );
    },
    inviteUser: function(machineId, user, accessType) {
      var data = {machineId: machineId, accesstype: accessType, emailaddress: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/machines/addExternalUser', data)
      .then(
        function(result) { return result.data;},
        function(reason) { return $q.reject(reason);}
      );
    },
    deleteUser: function(machineId, user) {
      var data = {machineId: machineId, accesstype: accessType, userId: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/machines/deleteUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason); }
      );
    },
    macineAccessRights: function() {
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
    updateUser: function(machineId, user, accessType) {
      var data = {machineId: machineId, accesstype: accessType, userId: user};
      return $http.post(cloudspaceconfig.apibaseurl + '/machines/updateUser', data)
      .then(
        function(result) { return result.data; },
        function(reason) { return $q.reject(reason); }
      );
    },
    addDisk: function(machineId, diskName, description, size, type) {
      var data = {machineId: machineId, diskName: diskName,
                  description: description, type: type, size: size};
      var url = cloudspaceconfig.apibaseurl + '/machines/addDisk';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    removeDisk: function(diskId, detach) {
      var data = {diskId: diskId, detach: detach};
      var url = cloudspaceconfig.apibaseurl + '/disks/delete';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    moveDisk: function(machineId, diskId) {
      var data = {diskId: diskId, machineId: machineId};
      var url = cloudspaceconfig.apibaseurl + '/machines/attachDisk';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    },
    resize: function(machineId, sizeId) {
      var data = {sizeId: sizeId, machineId: machineId};
      var url = cloudspaceconfig.apibaseurl + '/machines/resize';
      return $http.post(url, data).then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
})
.factory('Image', function($http, $q) {
  return {
    list: function(accountId, cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId, accountId: accountId};
      var url = cloudspaceconfig.apibaseurl + '/images/list';
      return $http.post(url, data).then(
        function(result){
          return result.data;
        },
        function(reason){
          return $q.reject(reason);
        }
      );
    }
  };
})
.factory('Size', function($http, $q) {
  return {
    list: function(cloudspaceId) {
      var data = {cloudspaceId: cloudspaceId};
      return $http.post(cloudspaceconfig.apibaseurl + '/sizes/list', data)
      .then(
        function(result) {
          return result.data;
        },function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
});
