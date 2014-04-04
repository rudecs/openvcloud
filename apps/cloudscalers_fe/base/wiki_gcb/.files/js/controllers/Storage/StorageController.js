angular.module('cloudscalers.controllers')
    .controller('StorageController', ['$scope', 'Storagebuckets',
        function ($scope, Storagebuckets) {
                Storagebuckets.listStorgaesByCloudSpace($scope.currentSpace.id).then(function(result) {
                    $scope.storages =result;
                });
        }
    ]);