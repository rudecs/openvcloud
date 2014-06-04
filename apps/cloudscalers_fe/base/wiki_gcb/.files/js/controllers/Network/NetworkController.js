angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout', '$sce',
        function ($scope, Networks, Machine, $modal, $timeout, $sce) {
            $scope.search = "";
            $scope.portforwardbyID = "";
            $scope.$watch('currentSpace.id',function(){
                if ($scope.currentSpace){
                    $scope.managementui = "http://" + $scope.currentSpace.publicipaddress + ":9080/webfig/";
                    Machine.list($scope.currentSpace.id).then(function(data) {
                      $scope.currentSpace.machines = data;
                    });
                }
            });

            var routerosController = function ($scope, $modalInstance) {
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
                // for load scope value in iframe
                $scope.trustSrc = function(src) {
                    return $sce.trustAsResourceUrl(src);
                }
            };
            $scope.routeros = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'routerosDialog.html',
                    controller: routerosController,
                    resolve: {},
                    scope: $scope
                });
            };
        }
    ]);
