angular.module('cloudscalers.controllers')
    .controller('ListDesktopBucketsController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.buckets = DesktopBucketService.getAll();
    }])