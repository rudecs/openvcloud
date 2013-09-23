cloudscalersControllers
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
    }]);
