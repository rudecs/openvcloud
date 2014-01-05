angular.module('cloudscalers.controllers')
    .controller('MachineEditController', 
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'confirm', '$modal', 'LoadingDialog',
                function($scope, $routeParams, $timeout, $location, Machine, confirm, $modal, LoadingDialog) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.tabactive = {};

        var changeSelectedTab = function(tab){
        	if (tab){
        		$scope.tabactive = {'actions': tab=='actions', 'console': tab == 'console', 'snapshots': tab=='snapshots', 'snapshots': tab=='snapshots', 'history': tab =='history'};
        	}
        }
        
        changeSelectedTab($routeParams.activeTab);
        
        var retrieveMachineHistory = function() {
            $scope.machineHistory = Machine.getHistory($routeParams.machineId, $scope.machineHistory);

            // Because ElasticSearch has a delay of maximum 1 second, the retrieved data may not be updated, so I retrieve it again after 1 second
            $timeout(function() {
                $scope.machineHistory = Machine.getHistory($routeParams.machineId, $scope.machineHistory);
            }, 2000)
        };
        retrieveMachineHistory();
        $scope.$watch('tabactive.history', function() {
            if (!$scope.tabactive.history)
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
            $scope.snapshots = Machine.listSnapshots($routeParams.machineId)
        }

        $scope.$watch('snapshotcreated', updatesnapshots, true);

        $scope.createSnapshot = function() {

        	var modalInstance = $modal.open({
      			templateUrl: 'createSnapshotDialog.html',
      			controller: CreateSnapshotController,
      			resolve: {
      			}
    		});

    		modalInstance.result.then(function (snapshotname) {
    			$scope.snapshotcreated = Machine.createSnapshot($scope.machine.id, snapshotname);
    		});

            LoadingDialog.show('Creating a snapshot', 1000);
        };

        $scope.rollbackSnapshot = function(snapshot) {
            Machine.rollbackSnapshot($scope.machine.id, snapshot.name);
            location.reload();
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

    		var modalInstance = $modal.open({
          			templateUrl: 'cloneMachineDialog.html',
          			controller: CloneMachineController,
          			resolve: {
          			}
        		});

        		modalInstance.result.then(function (cloneName) {
                    Machine.clone($scope.machine, cloneName);
                    $location.path("/list/");
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
                    //TODO show error
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
                    //TODO show error
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
                    //TODO show error
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
                    //TODO show error
                }
            );
        };

    }]);
