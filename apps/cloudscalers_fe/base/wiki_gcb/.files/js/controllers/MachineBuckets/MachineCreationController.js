cloudscalersControllers
    .controller('MachineCreationController', ['$scope', '$timeout', '$location', 'Machine', 'Size', 'Image', function($scope, $timeout, $location, Machine, Size, Image) {
        $scope.machine = {
            cloudspaceId: 1,
            name: '',
            description: '',
            sizeId: '',
            imageId: ''
        };

        $scope.sizes = Size.list();
        $scope.images = Image.list();

        $scope.saveNewMachine = function() {
            Machine.create($scope.machine.cloudspaceId, $scope.machine.name, $scope.machine.description, 
                           $scope.machine.sizeId, $scope.machine.imageId, $scope.machine.disksize);
            $location.path('/list');
        };

        $scope.isValid = function() {
            return $scope.machine.name !== '' && $scope.machine.sizeId !== '' && $scope.machine.imageId !== '';
        };

        $scope.$watch('images', function() {
            console.log('images changed ' + $('.nav-tabs a').length);
        });
    }]);
