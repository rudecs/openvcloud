angular.module('cloudscalers.controllers')
    .controller('PortforwardingController', ['$scope', 'Networks', 'Machine', '$modal', '$interval','$ErrorResponseAlert', 'CloudSpace','$timeout', '$routeParams', '$window' ,
        function ($scope, Networks, Machine, $modal, $interval,$ErrorResponseAlert, CloudSpace,$timeout, $routeParams, $window) {
            $scope.portforwarding = [];
            $scope.commonPortVar = "";

            $scope.$watch('currentSpace.acl', function () {
                if($scope.currentUser.username && $scope.currentSpace.acl && !$scope.currentUserAccessrightOnCloudSpace){
                    var currentUserAccessright =  _.find($scope.currentSpace.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; }).right.toUpperCase();
                    if(currentUserAccessright == "R"){
                        $scope.currentUserAccessrightOnCloudSpace = 'Read';
                    }else if( currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') == -1 && currentUserAccessright.indexOf('U') == -1){
                        $scope.currentUserAccessrightOnCloudSpace = "ReadWrite";
                    }else if(currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') != -1 && currentUserAccessright.indexOf('U') != -1){
                        $scope.currentUserAccessrightOnCloudSpace = "Admin";
                    }
                }
            });

            $scope.updatePortforwardList = function(){
              $scope.portforwardLoader = true;
              if($routeParams.machineId){
                Networks.listPortforwarding($scope.currentSpace.id, $routeParams.machineId).then(
                  function(data) {
                    $scope.portforwarding = data;
                    $scope.portforwardLoader = false;
                  },
                  function(reason) {
                    $ErrorResponseAlert(reason);
                    $scope.portforwardLoader = false;
                  }
                )
              }else{
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

            };

            $scope.updateData = function(){
            	Machine.list($scope.currentSpace.id).then(function(data) {
            		$scope.currentSpace.machines = data;
            	});
            	$scope.updatePortforwardList();
            }

            $scope.machineIsManageable = function(machine){
                return machine.status && machine.status != 'DESTROYED' && machine.status != 'ERROR';
            }

            var cloudspaceupdater;

            $scope.$watch('currentSpace.id + currentSpace.status',function(){
                if ($scope.currentSpace){
                	if ($scope.currentSpace.status != "DEPLOYED"){
                		if (!(angular.isDefined(cloudspaceupdater))){
                			cloudspaceupdater = $interval($scope.loadSpaces,5000);
                		}
                	}
                	else{
                		if (angular.isDefined(cloudspaceupdater)){
                			$interval.cancel(cloudspaceupdater);
                			cloudspaceupdater = undefined;
                		}
                		$scope.updateData();
                	}
                }
            });

            $scope.$on(
                    "$destroy",
                    function( event ) {
                    	if (angular.isDefined(cloudspaceupdater)){
                    		$interval.cancel(cloudspaceupdater );
                    		cloudspaceupdater = undefined;
                    	}
                    }
                );

            $scope.commonports = Networks.commonports();

            $scope.suggestCommonPorts = function(typedport){
            	$scope.commonPorts = Networks.commonports();
            };
            var addRuleController = function ($scope, $modalInstance) {
                $scope.updateData();
                $scope.$watch('currentSpace.machines', function () {
                  if($scope.currentSpace.machines){
                    $scope.manageableMachines = _.filter($scope.currentSpace.machines, function(machine){ return $scope.machineIsManageable(machine) == true; });
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
                $scope.updateCommonPorts = function () {
                    $scope.newRule.publicPort  = $scope.newRule.commonPort.port;
                    $scope.newRule.localPort = $scope.newRule.commonPort.port;
                };

                $scope.submit = function () {
                    var machineId;
                    if($routeParams.machineId){
                      machineId = $routeParams.machineId;
                    }else{
                      machineId = $scope.newRule.VM.id;
                    }
                  	Networks.createPortforward($scope.currentSpace.id, $scope.currentSpace.publicipaddress, $scope.newRule.publicPort, machineId, $scope.newRule.localPort, $scope.newRule.protocol).then(
                      function (result) {
                        $modalInstance.close({
                          statusMessage: "Port forward created."
                        });
                      	$scope.updatePortforwardList();
                      },
                      function(reason){
                      	$ErrorResponseAlert(reason);
                      }
                    );
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
                    $scope.message = true;
                    $scope.statusMessage = data.statusMessage;
                    $timeout(function() {
                        $scope.message = false;
                    }, 3000);
                });
            };

            var editRuleController = function ($scope, $modalInstance, editRule) {
                $scope.updateData();
                $scope.editRule = editRule;
                $scope.$watch('currentSpace.machines', '');

                $scope.delete = function () {
                    $scope.editRule.action = 'delete';
                    Networks.deletePortforward($scope.currentSpace.id, $scope.editRule.id).then(
                        function (result) {
                            $modalInstance.close($scope.editRule);
                            $scope.portforwarding = result.data;
                        	  $scope.updatePortforwardList();
                        },
                        function(reason){
                        	$ErrorResponseAlert(reason);
                        }
                    );
                };
                $scope.cancel = function () {
                      $modalInstance.dismiss('cancel');
                };
                $scope.updateCommonPorts = function () {
                      $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
                      $scope.editRule.localPort = $scope.editRule.commonPort.port;
                };

                $scope.update = function () {
                	$scope.editRule.action = 'update';
                  Networks.updatePortforward($scope.currentSpace.id, $scope.editRule.id, $scope.editRule.ip, $scope.editRule.publicPort, $scope.editRule.VM.id, $scope.editRule.localPort, $scope.editRule.protocol).then(
                      function (result) {
                        $modalInstance.close($scope.editRule);
                        $scope.portforwarding = result.data;
                        $scope.updatePortforwardList();
                      },
                      function(reason){
                        $ErrorResponseAlert(reason);
                      }
                  );
                };
            }

            $scope.tableRowClicked = function (index) {
              var uri = new URI($window.location);
              if(uri._parts.path.indexOf('Portforwarding') != -1){
                if($scope.currentUserAccessrightOnCloudSpace == 'Read'){
                  return;
                }
              }else{
                if($scope.currentUserAccess == 'Read'){
                  return;
                }
              }
            	var selectForwardRule = _.findWhere($scope.portforwarding, { id: parseInt(index.id) });
            	var editRule = {
                         id: index.id,
                         ip: selectForwardRule.publicIp,
                         publicPort: selectForwardRule.publicPort,
                         VM: {'name': selectForwardRule.vmName , 'id': selectForwardRule.vmid},
                         localPort: selectForwardRule.localPort,
                         protocol: selectForwardRule.protocol
                 };
            	var modalInstance = $modal.open({
            	  templateUrl: 'editPortForwardDialog.html',
            	  controller: editRuleController,
            	  scope: $scope ,
            	  resolve: {editRule: function(){ return editRule;}}
            	});
            	modalInstance.result.then(function(data){
                $scope.showStatusMessage = function() {
                    $scope.message = true;
                    $timeout(function() {
                        $scope.message = false;
                    }, 3000);
                }
            		if (data.action=='delete'){
                    $scope.statusMessage = 'Port forward removed.';
                    $scope.showStatusMessage();
            		}
            		else{
                    $scope.statusMessage = 'Port forward updated.';
                    $scope.showStatusMessage();
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
