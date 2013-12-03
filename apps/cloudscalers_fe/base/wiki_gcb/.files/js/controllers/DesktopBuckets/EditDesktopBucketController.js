angular.module('cloudscalers.controllers')
    .controller('EditDesktopBucketController', ['$scope', '$routeParams', 'DesktopBucketService', function($scope, $routeParams, DesktopBucketService) {
        if (DesktopBucketService.loadSettings())
            $scope.settings = DesktopBucketService.loadSettings();
        else 
            $scope.settings = {   
                domain: '',
                storage: 100,
                locations: [false, false, false],
            };

        $scope.isValid = function() {
            return $scope.settings.domain && $scope.settings.storage && _.any($scope.settings.locations);
        };

        $scope.save = function() {
            DesktopBucketService.saveSettings($scope.settings);
            location.href = "My Desktop Buckets";
        };
    }])
