cloudscalersControllers
    .controller('MachineCreationController', ['$scope', 'Machine', 'Size', 'Image', function($scope, Machine, Size, Image) {
        $scope.newMachine = {
            cloudspaceId: 1,
            name: '',
            description: '',
            sizeId: '',
            imageId: ''
        };

        $scope.sizes = Size.list();
        $scope.images = Image.list();

        $scope.saveNewMachine = function() {
            Machine.create($scope.newMachine.cloudspaceId, $scope.newMachine.name, $scope.newMachine.description, 
                           $scope.newMachine.sizeId, $scope.newMachine.imageId)
        };

        $scope.isValid = function() {
            return $scope.newMachine.name && $scope.newMachine.sizeId && $scope.newMachine.imageId;
        };
    }]);
