angular.module('cloudscalers.controllers')
    .controller('PortforwardingController', ['$scope', 'Networks', 'Machine', '$modal', '$interval','$ErrorResponseAlert','LoadingDialog', 'CloudSpace','$timeout', '$routeParams', '$window' ,
        function ($scope, Networks, Machine, $modal, $interval,$ErrorResponseAlert,LoadingDialog, CloudSpace,$timeout, $routeParams, $window) {
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
                var uri = new URI($window.location);
                if(uri._parts.path.indexOf('Portforwarding') > -1){
                  if($scope.currentUserAccessrightOnCloudSpace != 'Admin'){
                    uri.filename('Decks');
                    $window.location = uri.toString();
                  }
                }
            });

            $scope.updatePortforwardList = function(){
              if($routeParams.machineId){
                Networks.listPortforwarding($scope.currentSpace.id, $routeParams.machineId).then(
                  function(data) {
                    $scope.portforwarding = data;
                  },
                  function(reason) {
                    $ErrorResponseAlert(reason);
                  }
                )
              }else{
                Networks.listPortforwarding($scope.currentSpace.id).then(
                  function(data) {
                    $scope.portforwarding = data;
                  },
                  function(reason) {
                    $ErrorResponseAlert(reason);
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
                $scope.newRule = {
                    ip: $scope.currentSpace.publicipaddress,
                    publicPort: '',
                    VM: $scope.currentSpace.machines[0],
                    localPort: '',
                    commonPort: '',
                    protocol: 'tcp',
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
                    	vmname: $scope.newRule.VM.name,
                        protocol: $scope.newRule.protocol
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
                  if($routeParams.machineId){
                    var machineId = $routeParams.machineId;
                  }else{
                    var machineId = data.vmid;
                  }
                	Networks.createPortforward(data.cloudspaceId, data.publicipaddress, data.publicport, machineId, data.localport, data.protocol).then(
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
                      $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
                      $scope.editRule.localPort = $scope.editRule.commonPort.port;
                };

                $scope.update = function () {
                	$scope.editRule.action = 'update';
                    $modalInstance.close($scope.editRule);
                };
            }

            $scope.tableRowClicked = function (index) {
              var uri = new URI($window.location);
              if(uri._parts.path.indexOf('Portforwarding') == -1){
                if($scope.currentUserAccess != 'Admin'){
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
                        Networks.updatePortforward($scope.currentSpace.id, data.id, data.ip, data.publicPort, data.VM.id, data.localPort, data.protocol).then(
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
