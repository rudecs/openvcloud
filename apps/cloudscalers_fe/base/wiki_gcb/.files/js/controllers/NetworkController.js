
angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'NetworkBuckets', '$modal',
    	function ($scope, NetworkBuckets, $modal) {
            $scope.$watch('currentSpace.id',function(){
	    		if ($scope.currentSpace){
	    			$scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
	    		}
    		});
    		NetworkBuckets.listPortforwarding().then(function(data) {
                $scope.portforwarding = data;
            });
            var addRuleController = function ($scope, $modalInstance) {
                $scope.newRule = {
                    ip: '',
                    publicPort: '',
                    VM: '1',
                    localPort: ''
                };
                NetworkBuckets.commonports().then(function(data) {
                    $scope.commonports = data;
                });
                $scope.updatePorts = function () {
                    // $scope.newRule.publicPort  = $scope.selected;
                };
                $scope.submit = function () {
                    $modalInstance.close({
                        name: $scope.newRule.name,
                        accountId: $scope.newRule.account.id
                    });
                };
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
            };
            $scope.rulesPopup = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'rulesDialog.html',
                    controller: addRuleController,
                    resolve: {},
                    scope: $scope
                });

                modalInstance.result.then(function (space) {
                    LoadingDialog.show('Creating New Rule');
                    NetworkBuckets.create().then(
                        function () {
                            
                        },
                        function (result) {
                            LoadingDialog.hide();
                            //TODO: show error
                        }
                    );
                });
            };
            
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
    });