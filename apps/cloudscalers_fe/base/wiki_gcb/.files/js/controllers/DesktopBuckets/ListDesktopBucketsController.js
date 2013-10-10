cloudscalersControllers
    .controller('ListDesktopBucketsController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.buckets = DesktopBucketService.getAll();
        $scope.numOfDataLocations = function(bucket) {
            if (!bucket.locations || !bucket.locations.length)
                return 0;
            var numOfLocations = 0;
            for (var i = 0; i < bucket.locations.length; i++) {
                if (bucket.locations[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        }
    }])