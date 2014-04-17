angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout',
        function ($scope, Networks, Machine, $modal, $timeout) {
            $scope.search = "";
            $scope.portforwardbyID = "";
            $scope.$watch('currentSpace.id',function(){
                if ($scope.currentSpace){
                    $scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
                    Machine.list($scope.currentSpace.id).then(function(data) {
                      $scope.currentSpace.machines = data;
                    });
                }
            });
        }
    ]);
