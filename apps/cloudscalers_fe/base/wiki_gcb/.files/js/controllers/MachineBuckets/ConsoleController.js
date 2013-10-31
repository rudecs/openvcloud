
cloudscalersControllers
    .controller('ConsoleController', ['$scope','$routeParams', 'Machine'], function($scope, $routeParams, Machine) {
        $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
        $scope.novnc-connectioninfo = {}
        
        
    }]);