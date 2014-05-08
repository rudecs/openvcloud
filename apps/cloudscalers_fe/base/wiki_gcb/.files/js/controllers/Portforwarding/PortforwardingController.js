angular.module('cloudscalers.controllers')
    .controller('PortforwardingController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout','$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $timeout,$ErrorResponseAlert) {
            $scope.search = "";
            $scope.portforwardbyID = "";
            $scope.portforwarding = [];
            $scope.$watch('currentSpace.id',function(){
                if ($scope.currentSpace){
                    $scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
                    Machine.list($scope.currentSpace.id).then(function(data) {
                      $scope.currentSpace.machines = data;
                    });
                }
            });
            Networks.listPortforwarding($scope.currentSpace.id).then(function(data) {
                $scope.portforwarding = data;
            });

            Networks.commonports().then(function(data) {
                $scope.commonports = data;
            });

            var addRuleController = function ($scope, $modalInstance) {
                $scope.newRule = {
                    ip: $scope.currentSpace.publicipaddress,
                    publicPort: '',
                    VM: $scope.currentSpace.machines[0],
                    localPort: '',
                    commonPort: '',
                    // message: false,
                    statusMessage: ''
                };

                $scope.updateCommonPorts = function () {
                    $scope.newRule.publicPort  = $scope.newRule.commonPort.port;
                    $scope.newRule.localPort = $scope.newRule.commonPort.port;
                };

                $scope.submit = function () {
                    
                    $modalInstance.close({
                    	cloudspaceId: $scope.currentSpace.id,
                    	publicipaddress: $scope.currentSpace.publicipaddress,
                    	publicport: $scope.newRule.publicPort,
                    	vmid: $scope.newRule.VM.id,
                    	localport: $scope.newRule.localPort,
                    	vmname: $scope.newRule.VM.name
                    });
                };
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
            };
            $scope.portForwardPopup = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'portForwardDialog.html',
                    controller: addRuleController,
                    resolve: {},
                    scope: $scope
                });
                modalInstance.result.then(function(data){
                	Networks.createPortforward(data.cloudspaceId, data.publicipaddress, data.publicport, data.vmid, data.localport).then(
                            function (result) {
                                $scope.portforwarding.push({publicIp: data.publicipaddress, publicPort: data.publicport,
                                vmName: data.vmname, vmid: data.vmid, localPort: data.localport});
                            },
                            function(reason){
                            	$ErrorResponseAlert(reason);
                            }
                        );
                });
            };
            $scope.tableRowClicked = function (index) {
              var modalInstance = $modal.open({templateUrl: 'editPortForwardDialog.html', scope: $scope , resolve: {}});
              $scope.editRule = [];
              Networks.listPortforwarding($scope.currentSpace.id).then(function(data) {
                $scope.portforwardbyID = data;
                $scope.editRule = {
                    id: index.id,
                    ip: $scope.portforwardbyID[index.id].publicIp,
                    publicPort: $scope.portforwardbyID[index.id].publicPort,
                    VM: {'name': $scope.portforwardbyID[index.id].vmName , 'id': $scope.portforwardbyID[index.id].vmid},
                    localPort: $scope.portforwardbyID[index.id].localPort
                };
              });
              $scope.update = function () {
                console.log($scope.editRule.VM.id);
                  Networks.updatePortforward($scope.currentSpace.id, $scope.editRule.id, $scope.editRule.ip, $scope.editRule.publicPort, $scope.editRule.VM.id, $scope.editRule.localPort).then(
                      function (result) {
                          $scope.portforwarding = result.data;
                          $scope.search = $scope.portforwarding[0];
                          modalInstance.close({});
                          $scope.message = true;
                          $scope.statusMessage = "Saved!";
                          $timeout(function() {
                              $scope.message = false;
                          }, 3000);
                      }
                  );
              };
              $scope.delete = function () {
                  Networks.deletePortforward($scope.currentSpace.id, $scope.editRule.id).then(
                      function (result) {
                          $scope.portforwarding = result.data;
                          $scope.search = $scope.portforwarding[0];
                          modalInstance.close({});
                          $scope.message = true;
                          $scope.statusMessage = "Removed!";
                          $timeout(function() {
                              $scope.message = false;
                          }, 3000);
                      }
                  );
              };
              $scope.cancel = function () {
                    modalInstance.dismiss('cancel');
              };
              $scope.updateCommonPorts = function () {
                    $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
                    $scope.editRule.localPort = $scope.editRule.commonPort.port;
                };
            }

        }
    ]).filter('groupBy', function(){
        return function(list, group_by) {
        var filtered = [];
        var prev_item = null;
        var group_changed = false;
        var new_field = group_by + '_CHANGED';
        angular.forEach(list, function(item) {
            group_changed = false;
            if (prev_item !== null) {
                if (prev_item[group_by] !== item[group_by]) {
                    group_changed = true;
                }
            } else {
                group_changed = true;
            }
            if (group_changed) {
                item[new_field] = true;
            } else {
                item[new_field] = false;
            }
            filtered.push(item);
            prev_item = item;
        });
        return filtered;
        };
    }).filter('unique', function() {
       return function(collection, keyname) {
          var output = [],
              keys = [];

          angular.forEach(collection, function(item) {
              var key = item[keyname];
              if(keys.indexOf(key) === -1) {
                  keys.push(key);
                  output.push(item);
              }
          });

          return output;
       };
    }).directive('numbersOnly', function(){
   return {
     require: 'ngModel',
     link: function(scope, element, attrs, modelCtrl) {
       modelCtrl.$parsers.push(function (inputValue) {
           if (inputValue == undefined) return ''
           var transformedInput = inputValue.replace(/[^0-9]/g, '');
           if (transformedInput!=inputValue) {
              modelCtrl.$setViewValue(transformedInput);
              modelCtrl.$render();
           }

           return transformedInput;
       });
     }
   };
});
