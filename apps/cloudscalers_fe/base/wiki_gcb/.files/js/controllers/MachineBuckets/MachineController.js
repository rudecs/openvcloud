
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', 'Size', 'Image', function($scope, Machine, Size, Image) {
        $scope.machines = Machine.list(1);
        $scope.sizes = Size.list();
        $scope.images = Image.list();
        
        $scope.numOfDataLocations = function(machine) {
            return _.filter(machine.region, function(x) { return x; }).length;
        };
    }]);
