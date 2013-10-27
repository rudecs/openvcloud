
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', 'Size', 'Image', function($scope, Machine, Size, Image) {
        $scope.machines = Machine.list(1);
        $scope.sizes = Size.list();
        $scope.images = Image.list();
    }]);
