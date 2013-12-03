angular.module('cloudscalers.controllers')
    .controller('CreateDesktopBucketController', ['$scope', '$window', 'DesktopBucketService', function($scope, $window, DesktopBucketService) {
        var bucketId = $window.location.hash.replace('#', '').replace('/', '');
        $scope.bucket = DesktopBucketService.getById(bucketId);
        if (!$scope.bucket) {
            $scope.isNewBucket = true;
            $scope.bucket = { email: '', userType: '', id: Math.random()};
        } else {
            $scope.isNewBucket = false;
        }
        
        $scope.isValid = function() {
            return $scope.bucket.email && $scope.bucket.userType;
        };

        $scope.create = function() {
            DesktopBucketService.add($scope.bucket);
            $scope.bucket = { email: '', userType: '', id: Math.random() };
            $window.location.href = "My Desktop Buckets";
        };

        $scope.update = function() {
            DesktopBucketService.save($scope.bucket);
            $window.location.href = "My Desktop Buckets";  
        }
    }])