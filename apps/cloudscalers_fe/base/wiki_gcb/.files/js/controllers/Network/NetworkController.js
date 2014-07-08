angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout', '$sce', 'CloudSpace', '$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $timeout, $sce, CloudSpace, $ErrorResponseAlert) {
            $scope.search = "";
            $scope.portforwardbyID = "";

            $scope.getDefenseShield = function() {
                CloudSpace.getDefenseShield($scope.currentSpace.id).then(function(shieldobj) {
                    var tab = window.open(shieldobj.url, "autologin=" + shieldobj.user + "|" + shieldobj.password);
                    tab.focus();
                    $scope.disableAdvancedShieldConfiguration = true;
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
		
            };
        }
    ]);
