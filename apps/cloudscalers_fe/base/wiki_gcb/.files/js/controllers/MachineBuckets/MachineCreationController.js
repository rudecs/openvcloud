cloudscalersControllers
    .controller('MachineCreationController', ['$scope', '$timeout', '$location', '$window', 'Machine', 'Size', 'Image', function($scope, $timeout, $location, $window, Machine, Size, Image) {
        $scope.machine = {
            cloudspaceId: 1,
            name: '',
            description: '',
            sizeId: '',
            imageId: ''
        };

        $scope.sizes = Size.list();
        $scope.images = Image.list();
        $scope.numeral = $window.numeral;

        $scope.saveNewMachine = function() {
            Machine.create($scope.machine.cloudspaceId, $scope.machine.name, $scope.machine.description, 
                           $scope.machine.sizeId, $scope.machine.imageId, $scope.machine.disksize,
                           $scope.machine.archive,
                           $scope.machine.region, $scope.machine.replication);
            $location.path('/list');
        };

        $scope.isValid = function() {
            return $scope.machine.name !== '' && $scope.machine.sizeId !== '' && $scope.machine.imageId !== '';
        };
    }]);
