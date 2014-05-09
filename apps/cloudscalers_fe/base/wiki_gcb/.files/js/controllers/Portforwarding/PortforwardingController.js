angular.module('cloudscalers.controllers')
    .controller('PortforwardingController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout','$ErrorResponseAlert','LoadingDialog',
        function ($scope, Networks, Machine, $modal, $timeout,$ErrorResponseAlert,LoadingDialog) {
            $scope.portforwarding = [];
            $scope.commonPortVar = "";
            $scope.$watch('currentSpace.id',function(){
                if ($scope.currentSpace){
                    Machine.list($scope.currentSpace.id).then(function(data) {
                      $scope.currentSpace.machines = data;
                    });
                }
            });
            
            $scope.updatePortforwardList = function(){
            	Networks.listPortforwarding($scope.currentSpace.id).then(
            			function(data) {
            				$scope.portforwarding = data;
            			},
            			function(reason) {
            				$ErrorResponseAlert(reason);
            			}
            	);
            };
            
            $scope.updatePortforwardList();

            Networks.commonports().then(function(data) {
                $scope.commonports = data;
            });

            // commonports auto suggest
            Networks.commonports("...").then(function(data) {
              $scope.commonPorts = data;
            });

            $scope.suggestCommonPorts = function(typedport){
              Networks.commonports(typedport).then(function(data) {
                $scope.commonPorts = data;
              });
            };
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
                	LoadingDialog.show('Creating');
                	Networks.createPortforward(data.cloudspaceId, data.publicipaddress, data.publicport, data.vmid, data.localport).then(
                            function (result) {
                            	LoadingDialog.hide();
                            	$scope.updatePortforwardList();
                            },
                            function(reason){
                            	LoadingDialog.hide();
                            	$ErrorResponseAlert(reason);
                            }
                        );
                });
            };
            
            var editRuleController = function ($scope, $modalInstance, editRule) {
            	$scope.editRule = editRule;

                $scope.delete = function () {
                  $scope.editRule.action = 'delete';
                    $modalInstance.close($scope.editRule);
                };
                $scope.cancel = function () {
                      $modalInstance.dismiss('cancel');
                };
                $scope.updateCommonPorts = function () {
                  alert('sssaddas')
                      $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
                      $scope.editRule.localPort = $scope.editRule.commonPort.port;
                };
                  
                $scope.update = function () {
                	$scope.editRule.action = 'update';
                    $modalInstance.close($scope.editRule);
                };
            }
            	
    
            
            
            $scope.tableRowClicked = function (index) {
            	var selectForwardRule = $scope.portforwarding[index.id];
            	var editRule = {
                         id: index.id,
                         ip: selectForwardRule.publicIp,
                         publicPort: selectForwardRule.publicPort,
                         VM: {'name': selectForwardRule.vmName , 'id': selectForwardRule.vmid},
                         localPort: selectForwardRule.localPort
                 };
            	var modalInstance = $modal.open({
            	  templateUrl: 'editPortForwardDialog.html',
            	  controller: editRuleController,
            	  scope: $scope , 
            	  resolve: {editRule: function(){ return editRule;}}
            	});
            	modalInstance.result.then(function(data){
            		LoadingDialog.show('Deleting');
            		if (data.action=='delete'){
                        Networks.deletePortforward($scope.currentSpace.id, data.id).then(
                            function (result) {
                            	$scope.updatePortforwardList();
                            	LoadingDialog.hide();
                                $scope.portforwarding = result.data;
                                $scope.message = true;
                                $scope.statusMessage = "Removed";
                                $timeout(function() {
                                    $scope.message = false;
                                }, 3000);
                            },
                            function(reason){
                            	LoadingDialog.hide();
                            	$ErrorResponseAlert(reason);
                            }
                        );
            		}
            		else{
            			LoadingDialog.show('Updating');
                        Networks.updatePortforward($scope.currentSpace.id, data.id, data.ip, data.publicPort, data.VM.id, data.localPort).then(
                            function (result) {
                            	$scope.updatePortforwardList();
                            	LoadingDialog.hide();
                                $scope.portforwarding = result.data;
                                $scope.message = true;
                                $scope.statusMessage = "Updated";
                                $timeout(function() {
                                    $scope.message = false;
                                }, 3000);
                            }, 
                            function(reason){
                            	LoadingDialog.hide();
                            	$ErrorResponseAlert(reason);
                            }
                        );
            		}
            	});
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
}).filter('groupBy', function(){
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
    });
