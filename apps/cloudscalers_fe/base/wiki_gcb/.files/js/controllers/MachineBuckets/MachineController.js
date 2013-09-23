
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', function($scope, Machine) {
        $scope.buckets = Machine.list(0);
        
        $scope.numOfDataLocations = function(bucket) {
            var numOfLocations = 0;
            for (var i = 0; i < bucket.region.length; i++) {
                if (bucket.region[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        };
    }]);
