angular.module('cloudscalers.controllers')
    .controller('CreateDesktopBucketController', ['$scope', '$window', 'DesktopBucketService', function($scope, $window, DesktopBucketService) {
        $scope.newUser = { email: '', userType: '', id: Math.random()};
        
        $scope.isValid = function() {
            return $scope.newUser.email && $scope.newUser.userType;
        };

        $scope.create = function() {
            DesktopBucketService.add($scope.newUser);
            $scope.newUser = { email: '', userType: '', id: Math.random() };
            $window.location.href = "My Desktop Buckets";
        };
    }])