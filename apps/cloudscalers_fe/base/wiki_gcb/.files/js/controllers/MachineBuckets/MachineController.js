
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', function($scope, Machine) {
        $scope.machines = Machine.list(0);
        
        $scope.numOfDataLocations = function(machine) {
            return _.filter(machine.region, function(x) { return x; }).length;
        };
    }]);
