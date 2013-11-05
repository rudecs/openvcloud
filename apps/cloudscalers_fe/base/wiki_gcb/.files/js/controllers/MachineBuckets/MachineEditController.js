cloudscalersControllers
    .controller('MachineEditController', 
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'Image', 'Size', 'confirm', '$modal', 
                function($scope, $routeParams, $timeout, $location, Machine, Image, Size, confirm, $modal) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.machine.history = [{event: 'Created', initiated: getFormattedDate(), user: 'Admin'}];
        $scope.oldMachine = {};
        $scope.snapshots = Machine.listSnapshots($routeParams.machineId);

        $scope.sizes = Size.list();
        $scope.images = Image.list();
        $scope.imagesList = [];

        $scope.$watch('images', function() {
            $scope.imagesList = _.flatten(_.values(_.object($scope.images)));
        });

        $scope.$watch('machine', function() {
            angular.copy($scope.machine, $scope.oldMachine);
        }, true);

        $scope.destroy = function() {
            if (confirm('Are you sure you want to destroy this machine?')) {
                Machine.delete($scope.machine.id);
                $scope.machine.status = 'DESTROYED';
                $location.path("/list");
            }
        };

	var CreateSnapshotController = function ($scope, $modalInstance) {

		$scope.snapshotname= '';

  		$scope.ok = function () {
    			$modalInstance.close($scope.snapshotname);
  		};

  		$scope.cancel = function () {
    			$modalInstance.dismiss('cancel');
  		};
	};

        $scope.createSnapshot = function() {

        	var modalInstance = $modal.open({
      			templateUrl: 'createSnapshotDialog.html',
      			controller: CreateSnapshotController,
      			resolve: {
      			}
    		});

    		modalInstance.result.then(function (snapshotname) {
    			Machine.createSnapshot($scope.machine.id, snapshotName);
    		});

            showLoading('Creating a snapshot');
        };

        $scope.rollbackSnapshot = function(snapshot) {
            $scope.machine.history.push({event: 'Restored from snapshot', initiated: getFormattedDate(), user: 'Admin'});
            Machine.rollbackSnapshot($scope.machine.id, snapshot);
            location.reload();
        };

        $scope.deleteSnapshot = function(snapshot) {
            $scope.machine.history.push({event: 'Delete snapshot', initiated: getFormattedDate(), user: 'Admin'});
            Machine.deleteSnapshot($scope.machine.id, snapshot);
            location.reload();
        };

        
        

    	var RenameMachineController= function ($scope, $modalInstance) {

    		$scope.machineName = '';

      		$scope.ok = function () {
        			$modalInstance.close($scope.machineName);
      		};

      		$scope.cancel = function () {
        			$modalInstance.dismiss('cancel');
      		};
    	};
        
        
        
        
        $scope.renameMachine = function() {

    		var modalInstance = $modal.open({
          			templateUrl: 'renameMachineDialog.html',
          			controller: RenameMachineController,
          			resolve: {
          			}
        		});

        		modalInstance.result.then(function (newName) {
                    Machine.rename($scope.machine, newName);
        		});

        };

    	var CloneMachineController= function ($scope, $modalInstance) {

    		$scope.cloneName = '';

      		$scope.ok = function () {
        			$modalInstance.close($scope.cloneName);
      		};

      		$scope.cancel = function () {
        			$modalInstance.dismiss('cancel');
      		};
    	};
    	
        $scope.cloneMachine = function() {

    		var modalInstance = $modal.open({
          			templateUrl: 'cloneMachineDialog.html',
          			controller: ConeMachineController,
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
            showLoading('Starting...');
        };

         $scope.stop = function() {
            $scope.machine.history.push({event: 'Stopping machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.stop($scope.machine);
            showLoading('Stopping ...');
        };

        $scope.pause = function() {
            $scope.machine.history.push({event: 'Pausing machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.pause($scope.machine);
            showLoading('Pausing...');
        };

        $scope.resume = function() {
            $scope.machine.history.push({event: 'Resuming machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.resume($scope.machine);
            showLoading('Resuming...');
        };

    }]);
