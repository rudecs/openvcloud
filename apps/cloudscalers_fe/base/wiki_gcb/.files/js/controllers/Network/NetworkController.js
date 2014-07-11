angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout', '$sce', 'CloudSpace', '$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $timeout, $sce, CloudSpace, $ErrorResponseAlert) {

            var routerosController = function ($scope, $modalInstance) {
                $scope.cancel = function () {
            		$modalInstance.dismiss('cancel');
            	};
            	var defenseshieldautologin =  "autologin=" + $scope.defenseshield.user + "|" + $scope.defenseshield.password;
                $scope.defenseshieldframe = $sce.trustAsHtml('<iframe name="' + defenseshieldautologin + '" src="' + $scope.defenseshield.url +'" style="width:100%;height:80%"></iframe>');
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
