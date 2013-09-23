cloudscalersControllers
    .controller('MachineEditController', ['$scope', '$routeParams', 'Machine', function($scope, $routeParams, Machine) {
        $scope.machine = Machine.get($routeParams.machineId);
    }]);