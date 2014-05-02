angular.module('cloudscalers.controllers')
    .controller('StorageController', ['$scope', 'StorageService',
        function ($scope, StorageService) {
    			StorageService.listS3Buckets($scope.currentSpace.id).then(function(result) {
                    $scope.storages = result;
                }, function(reason){});
        }
    ]);