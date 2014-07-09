angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout', '$sce', 'CloudSpace', '$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $timeout, $sce, CloudSpace, $ErrorResponseAlert) {

            var routerosController = function ($scope, $modalInstance) {
                $scope.cancel = function () {
            		$modalInstance.dismiss('cancel');
            	};
		$scope.defenseshieldautologin =  "autologin=" + $scope.defenseshield.user + "|" + $scope.defenseshield.password;
                $scope.defenseshieldurl =$sce.trustAsResourceUrl($scope.defenseshield.url);
                }
            };

	    $scope.showDefenseShield = function(){
		CloudSpace.getDefenseShield($scope.currentSpace.id).then(function(shieldobj) {
		    	$scope.defenseshield = shieldobj;
	    		var modalInstance = $modal.open({
                   		templateUrl: 'routerosDialog.html',
                    		controller: routerosController,
                    		resolve: {},
                    		scope: $scope
                	});
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });


	    };

        }
    ]);
