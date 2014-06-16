angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout', '$sce', 'CloudSpace',
        function ($scope, Networks, Machine, $modal, $timeout, $sce, CloudSpace) {
            $scope.search = "";
            $scope.portforwardbyID = "";
            //$scope.$watch('currentSpace.id',function(){
            //    if ($scope.currentSpace){
            //        $scope.managementui = "http://" + $scope.currentSpace.publicipaddress + ":9080/webfig/";
            //        Machine.list($scope.currentSpace.id).then(function(data) {
            //          $scope.currentSpace.machines = data;
            //        });
            //    }
            //});
            //
            $scope.getDefenseShield = function() {
                CloudSpace.getDefenseShield($scope.currentSpace.id).then(function(shieldobj) {
                    window.open(shieldobj.url, "autologin=" + shieldobj.user + "|" + shieldobj.password, "width=400, height=400");
                },
                function(reason){
                    console.log(reason);
                });
            };

            //var routerosController = function ($scope, $modalInstance) {
            //    $scope.cancel = function () {
            //        $modalInstance.dismiss('cancel');
            //    };
            //    // for load scope value in iframe
            //    $scope.trustSrc = function(src) {
            //        return $sce.trustAsResourceUrl(src);
            //    }
            //};
            //$scope.routeros = function () {
            //    var modalInstance = $modal.open({
            //        templateUrl: 'routerosDialog.html',
            //        controller: routerosController,
            //        resolve: {},
            //        scope: $scope
            //    });
            //};
        }
    ]);
