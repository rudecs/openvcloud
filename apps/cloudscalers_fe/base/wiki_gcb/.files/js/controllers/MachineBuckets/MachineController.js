
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', function($scope, Machine) {
        $scope.buckets = Machine.list(1);
        
        $scope.numOfDataLocations = function(bucket) {
            return _.filter(bucket.region, function(x) { return x; }).length;
        };
    }]);
