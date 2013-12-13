angular.module('cloudscalers.controllers')
    .controller('MachineEditController', 
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'confirm', '$modal', 'LoadingDialog',
                function($scope, $routeParams, $timeout, $location, Machine, confirm, $modal, LoadingDialog) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.machine.history = [{event: 'Created', initiated: getFormattedDate(), user: 'Admin'}];
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
            if (confirm('Are you sure you want to destroy this machine?')) {
                Machine.delete($scope.machine.id);
                var machine = _.findWhere($scope.machines, {id: $scope.machine.id});
                if (machine){
                	machine.status = 'DESTROYED';
                }
                $location.path("/list");
            }
        };

	var CreateSnapshotController = function ($scope, $modalInstance) {

		$scope.snapshotname= '';

        $scope.submit = function (result) {
        	$modalInstance.close(result);
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

            LoadingDialog.show('Creating a snapshot');
        };

        $scope.rollbackSnapshot = function(snapshot) {
            $scope.machine.history.push({event: 'Restored from snapshot', initiated: getFormattedDate(), user: 'Admin'});
            Machine.rollbackSnapshot($scope.machine.id, snapshot.name);
            location.reload();
        };

        $scope.deleteSnapshot = function(snapshot) {
            $scope.machine.history.push({event: 'Delete snapshot', initiated: getFormattedDate(), user: 'Admin'});
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
            $scope.machine.history.push({event: 'Started', initiated: getFormattedDate(), user: 'Admin'});
            Machine.start($scope.machine);
            LoadingDialog.show('Starting...');
            $scope.tabactive = {'actions': false, 'console': true, 'snapshots': false, 'changelog': false};
        };

         $scope.stop = function() {
            $scope.machine.history.push({event: 'Stopping machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.stop($scope.machine);
            LoadingDialog.show('Stopping ...');
        };

        $scope.pause = function() {
            $scope.machine.history.push({event: 'Pausing machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.pause($scope.machine);
            LoadingDialog.show('Pausing...');
        };

        $scope.resume = function() {
            $scope.machine.history.push({event: 'Resuming machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.resume($scope.machine);
            LoadingDialog.show('Resuming...');
        };

    }]);
