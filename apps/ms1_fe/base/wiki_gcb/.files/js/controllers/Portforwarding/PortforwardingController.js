(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('PortforwardingController', PortforwardingController)
    .filter('groupBy', groupBy)
    .filter('unique', unique)
    .directive('numbersOnly', numbersOnly);

  function PortforwardingController($scope, Networks, Machine, $modal, $interval,
    $ErrorResponseAlert, CloudSpace, $timeout, $routeParams, $window) {
    var cloudspaceupdater;
    $scope.portforwarding = [];
    $scope.commonPortVar = '';

    $scope.updatePortforwardList = updatePortforwardList;
    $scope.updateData = updateData;
    $scope.machineIsManageable = machineIsManageable;
    $scope.commonports = Networks.commonports();
    $scope.suggestCommonPorts = suggestCommonPorts;
    $scope.portForwardPopup = portForwardPopup;
    $scope.tableRowClicked = tableRowClicked;

    $scope.$watch('currentSpace.id + currentSpace.status', currentSpaceIdAndStatus);
    $scope.$on('$destroy', destroy);

    function updatePortforwardList() {
      $scope.portforwardLoader = true;
      if ($routeParams.machineId) {
        Networks.listPortforwarding($scope.currentSpace.id, $routeParams.machineId).then(
            function(data) {
              $scope.portforwarding = data;
              $scope.portforwardLoader = false;
            },
            function(reason) {
              $ErrorResponseAlert(reason);
              $scope.portforwardLoader = false;
            }
          );
      }else {
        Networks.listPortforwarding($scope.currentSpace.id).then(
            function(data) {
              $scope.portforwarding = data;
              $scope.portforwardLoader = false;
            },
            function(reason) {
              $ErrorResponseAlert(reason);
              $scope.portforwardLoader = false;
            }
          );
      }
    }

    function updateData() {
      Machine.list($scope.currentSpace.id).then(function(data) {
        $scope.currentSpace.machines = data;
      });
      $scope.updatePortforwardList();
    }

    function machineIsManageable(machine) {
      return machine.status && machine.status !== 'DESTROYED' && machine.status !== 'ERROR';
    }

    function suggestCommonPorts() {
      $scope.commonPorts = Networks.commonports();
    }

    function addRuleController($scope, $modalInstance) {
      $scope.updateData();
      $scope.$watch('currentSpace.machines', function() {
          if ($scope.currentSpace.machines) {
            $scope.manageableMachines = _.filter($scope.currentSpace.machines, function(machine) {
              return $scope.machineIsManageable(machine) === true;
            });
            $scope.newRule = {
              ip: $scope.currentSpace.publicipaddress,
              publicPort: '',
              VM: $scope.manageableMachines[0],
              localPort: '',
              commonPort: '',
              protocol: 'tcp',
              statusMessage: ''
            };
          }
        });
      $scope.updateCommonPorts = function() {
          $scope.newRule.publicPort = $scope.newRule.commonPort.port;
          $scope.newRule.localPort = $scope.newRule.commonPort.port;
        };

      $scope.submit = function() {
          var machineId;
          if ($routeParams.machineId) {
            machineId = $routeParams.machineId;
          }else {
            machineId = $scope.newRule.VM.id;
          }
          Networks.createPortforward($scope.currentSpace.id, $scope.currentSpace.publicipaddress,
            $scope.newRule.publicPort, machineId, $scope.newRule.localPort,
            $scope.newRule.protocol).then(
              function() {
                $modalInstance.close({
                  statusMessage: 'Port forward created.'
                });
                $scope.updatePortforwardList();
              },
              function(reason) {
                $ErrorResponseAlert(reason);
              }
            );
        };
      $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
        };
    }

    function portForwardPopup() {
      var modalInstance = $modal.open({
          templateUrl: 'portForwardDialog.html',
          controller: addRuleController,
          resolve: {},
          scope: $scope
        });

      modalInstance.result.then(function(data) {
          $scope.message = true;
          $scope.statusMessage = data.statusMessage;
          $timeout(function() {
            $scope.message = false;
          }, 3000);
        });
    }

    function editRuleController($scope, $modalInstance, editRule) {
      $scope.updateData();
      $scope.editRule = editRule;
      $scope.$watch('currentSpace.machines', '');

      $scope.delete = function() {
          $scope.editRule.action = 'delete';
          Networks.deletePortforward($scope.currentSpace.id, $scope.editRule.ip, $scope.editRule.publicPort).then(
            function(result) {
              $modalInstance.close($scope.editRule);
              $scope.portforwarding = result.data;
              $scope.updatePortforwardList();
            },
            function(reason) {
              $ErrorResponseAlert(reason);
            }
          );
        };
      $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
        };
      $scope.updateCommonPorts = function() {
          $scope.editRule.publicPort = $scope.editRule.commonPort.port;
          $scope.editRule.localPort = $scope.editRule.commonPort.port;
        };

      $scope.update = function() {
          $scope.editRule.action = 'update';
          Networks.updatePortforward($scope.currentSpace.id, $scope.editRule.id,
            $scope.editRule.ip, $scope.editRule.publicPort, $scope.editRule.VM.id,
            $scope.editRule.localPort, $scope.editRule.protocol).then(
              function(result) {
                $modalInstance.close($scope.editRule);
                $scope.portforwarding = result.data;
                $scope.updatePortforwardList();
              },
              function(reason) {
                $ErrorResponseAlert(reason);
              }
          );
        };
    }

    function tableRowClicked(index) {
      var uri = new URI($window.location);
      if (uri._parts.path.indexOf('Portforwarding') !== -1) {
        if ($scope.currentUser.acl.cloudspace < 2) {
          return;
        }
      }else {
        if ($scope.currentUser.acl.machine < 2) {
          return;
        }
      }
      var selectForwardRule = _.findWhere($scope.portforwarding, {id: parseInt(index.id)});
      var editRule = {
          id: index.id,
          ip: selectForwardRule.publicIp,
          publicPort: selectForwardRule.publicPort,
          VM: {'name': selectForwardRule.machineName , 'id': selectForwardRule.machineId},
          localPort: selectForwardRule.localPort,
          protocol: selectForwardRule.protocol
        };

      var modalInstance = $modal.open({
          templateUrl: 'editPortForwardDialog.html',
          controller: editRuleController,
          scope: $scope ,
          resolve: {editRule: function() { return editRule;}}
        });
      modalInstance.result.then(function(data) {
          $scope.showStatusMessage = function() {
            $scope.message = true;
            $timeout(function() {
              $scope.message = false;
            }, 3000);
          };
          if (data.action === 'delete') {
            $scope.statusMessage = 'Port forward removed.';
            $scope.showStatusMessage();
          } else {
            $scope.statusMessage = 'Port forward updated.';
            $scope.showStatusMessage();
          }
        });
    }

    function destroy() {
      if (angular.isDefined(cloudspaceupdater)) {
        $interval.cancel(cloudspaceupdater);
        cloudspaceupdater = undefined;
      }
    }

    function currentSpaceIdAndStatus() {
      if ($scope.currentSpace) {
        if ($scope.currentSpace.status !== 'DEPLOYED') {
          if (!(angular.isDefined(cloudspaceupdater))) {
            cloudspaceupdater = $interval($scope.loadSpaces,5000);
          }
        } else {
          if (angular.isDefined(cloudspaceupdater)) {
            $interval.cancel(cloudspaceupdater);
            cloudspaceupdater = undefined;
          }
          $scope.updateData();
        }
      }
    }
  }

  function groupBy() {
    return function(list, groupBy) {
        var filtered = [];
        var prevItem = null;
        var groupChanged = false;
        var newField = groupBy + '_CHANGED';
        angular.forEach(list, function(item) {
          groupChanged = false;
          if (prevItem !== null) {
            if (prevItem[groupBy] !== item[groupBy]) {
              groupChanged = true;
            }
          } else {
            groupChanged = true;
          }
          if (groupChanged) {
            item[newField] = true;
          } else {
            item[newField] = false;
          }
          filtered.push(item);
          prevItem = item;
        });
        return filtered;
      };
  }

  function unique() {
    return function(collection, keyname) {
      var output = [];
      var keys = [];

      angular.forEach(collection, function(item) {
        var key = item[keyname];
        if (keys.indexOf(key) === -1) {
          keys.push(key);
          output.push(item);
        }
      });

      return output;
    };
  }

  function numbersOnly() {
    return {
      require: 'ngModel',
      link: function(scope, element, attrs, modelCtrl) {
        modelCtrl.$parsers.push(function(inputValue) {
          if (inputValue === undefined) { return ''; }
          var transformedInput = inputValue.replace(/[^0-9]/g, '');
          if (transformedInput !== inputValue) {
            modelCtrl.$setViewValue(transformedInput);
            modelCtrl.$render();
          }
          if (parseInt(inputValue) > 65535) {
            modelCtrl.$setViewValue(modelCtrl.$modelValue);
            modelCtrl.$render();
            return modelCtrl.$modelValue;
          }

          return transformedInput;
        });
      }
    };
  }
})();
