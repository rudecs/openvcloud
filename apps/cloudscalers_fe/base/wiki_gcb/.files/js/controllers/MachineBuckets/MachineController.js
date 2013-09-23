
myAppControllers
    .controller('MachineController', ['$scope', 'Machine', function($scope, Machine) {
        $scope.buckets = Machine.list(0);
        
        $scope.numOfDataLocations = function(bucket) {
            var numOfLocations = 0;
            for (var i = 0; i < bucket.region.length; i++) {
                if (bucket.region[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        };
    }])

    .controller('MachineCreationController', ['$scope', 'Machine', function($scope, Machine) {
        $scope.newMachine = {
            cloudspaceId: 1,
            name: '',
            description: '',
            sizeId: 1,
            imageId: 2
        };

        $scope.saveNewMachine = function() {
            Machine.create($scope.newMachine.cloudspaceId, $scope.newMachine.name, $scope.newMachine.description, 
                           $scope.newMachine.sizeId, $scope.newMachine.imageId)
        };
    }])

    .controller('MachineEditController', ['$scope', '$routeParams', 'Machine', function($scope, $routeParams, Machine) {
        $scope.machine = Machine.get($routeParams.machineId);
    }]);