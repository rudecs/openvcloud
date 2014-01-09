angular.module('cloudscalers.controllers')
    .controller('MachineEditController', 
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'confirm', '$alert', '$modal', 'LoadingDialog',
                function($scope, $routeParams, $timeout, $location, Machine, confirm, $alert, $modal, LoadingDialog) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.tabactive = {};

        var changeSelectedTab = function(tab){
        	if (tab){
        		$scope.tabactive = {actions: tab=='actions', console: tab == 'console', snapshots: tab=='snapshots', changelog: tab=='changelog'};
        	}
        }
        
        changeSelectedTab($routeParams.activeTab);
        
        var retrieveMachineHistory = function() {
            if (!$scope.machineHistory)
                $scope.machineHistory = {};
            
            Machine.getHistory($routeParams.machineId)
                .success(function(data, status, headers, config) {
                    if (data == 'None') {
                        $scope.machineHistory.error = status;
                        $scope.machineHistory.history = [];
                    } else {
                        $scope.machineHistory.history = _.sortBy(data, function(h) { return -h._source.epoch; });
                        $scope.machineHistory.error = undefined;
                    }
                }).error(function (data, status, headers, config) {
                    $scope.machineHistory.error = status;
                    $scope.machineHistory.history = [];    
                });
        };
        
        $scope.$watch('tabactive.changelog', function() {
            if (!$scope.tabactive.changelog)
                return;
            retrieveMachineHistory();
        }, true);
        
        $scope.oldMachine = {};
        $scope.snapshots = Machine.listSnapshots($routeParams.machineId);

        $scope.imagesList = [];
        $scope.machineinfo = {};

        var updateMachineSize = function(){
            $scope.machineinfo = {};
            size = _.findWhere($scope.sizes, { id: $scope.machine.sizeid });
            $scope.machineinfo['size'] = size;
            image = _.findWhere($scope.images, { id: $scope.machine.imageid });
            $scope.machineinfo['image'] = image;
            $scope.machineinfo['storage'] = $scope.machine.storage;
        };

        $scope.$watch('images', function() {
            $scope.imagesList = _.flatten(_.values(_.object($scope.images)));
        });

        $scope.$watch('machine', function() {
            angular.copy($scope.machine, $scope.oldMachine);
        }, true);

        $scope.$watch('machine', updateMachineSize, true);
        $scope.$watch('sizes', updateMachineSize, true);
        $scope.$watch('images', updateMachineSize, true);

        $scope.destroy = function() {
            var modalInstance = $modal.open({
                templateUrl: 'destroyMachineDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                Machine.delete($scope.machine.id);
                var machine = _.findWhere($scope.machines, {id: $scope.machine.id});
                if (machine){
                    machine.status = 'DESTROYED';
                }
                $location.path("/list");
            });
        };

    	var CreateSnapshotController = function ($scope, $modalInstance) {

    		$scope.snapshotname= '';

            $scope.submit = function (result) {
            	$modalInstance.close(result.newSnapshotName);
            };

            $scope.cancel = function () {
            	$modalInstance.dismiss('cancel');
            };
    	};
        var updatesnapshots = function(){
            $scope.snapshots = Machine.listSnapshots($routeParams.machineId);
        }

        $scope.$watch('tabactive.snapshots', function() {
            if (!$scope.tabactive.snapshots)
                return;
            updatesnapshots();
        }, true);
        
        $scope.createSnapshot = function() {

        	if ($scope.machine.status != "HALTED"){
        		$alert("A snapshot can only be taken from a stopped machine bucket.");
        		return;
        	}
        	
        	var modalInstance = $modal.open({
      			templateUrl: 'createSnapshotDialog.html',
      			controller: CreateSnapshotController,
      			resolve: {
      			}
    		});

    		modalInstance.result.then(function (snapshotname) {
                LoadingDialog.show('Creating snapshot');
    			Machine.createSnapshot($scope.machine.id, snapshotname).then(
					function(result){
						LoadingDialog.hide();
					},
					function(reason){
						LoadingDialog.hide();
						$alert(reason.data);
                    }
				);
    		});
        };

        $scope.rollbackSnapshot = function(snapshot) {

        	if ($scope.machine.status != "HALTED"){
        		$alert("A snapshot can only be rolled back to a stopped machine bucket.");
        		return;
        	}

            LoadingDialog.show('Rolling back snapshot');
            Machine.rollbackSnapshot($scope.machine.id, snapshot.name).then(
            		function(result){
						LoadingDialog.hide();
			            location.reload();
					}, function(reason){
						LoadingDialog.hide();
						$alert(reason.data);
                    }
            	) ;
        };

        $scope.deleteSnapshot = function(snapshot) {
            Machine.deleteSnapshot($scope.machine.id, snapshot.name);
            location.reload();
        };

        
    	var CloneMachineController= function ($scope, $modalInstance) {
        	
    		$scope.clone ={name: ''};

      		$scope.ok = function () {
        			$modalInstance.close($scope.clone.name);
      		};

      		$scope.cancel = function () {
        			$modalInstance.dismiss('cancel');
      		};
    	};
    	
        $scope.cloneMachine = function() {

        	if ($scope.machine.status != "HALTED"){
        		$alert("A clone can only be taken from a stopped machine bucket.");
        		return;
        	}
    		var modalInstance = $modal.open({
          			templateUrl: 'cloneMachineDialog.html',
          			controller: CloneMachineController,
          			resolve: {
          			}
        		});

        		modalInstance.result.then(function (cloneName) {
                    LoadingDialog.show('Creating clone');
                    Machine.clone($scope.machine, cloneName).then(
    					function(result){
    						LoadingDialog.hide();
    	                    $location.path("/list/");
    					},
    					function(reason){
    						LoadingDialog.hide();
    						$alert(reason.data);
                        }
    				);
        		});
        };
        
        $scope.start = function() {
            LoadingDialog.show('Starting');
            Machine.start($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    changeSelectedTab('console');
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data.backtrace);
                }
            );

        };

         $scope.stop = function() {
            LoadingDialog.show('Stopping');
             Machine.stop($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data);
                }
            );
        };

        $scope.pause = function() {
            LoadingDialog.show('Pausing');
            Machine.pause($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data);
                }
            );
        };

        $scope.resume = function() {
            LoadingDialog.show('Resuming');
            Machine.resume($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data);
                }
            );
        };

    }]);
