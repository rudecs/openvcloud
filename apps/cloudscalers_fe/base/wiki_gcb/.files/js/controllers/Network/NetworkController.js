angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'Networks', 'Machine', '$modal', '$interval', '$sce', 'CloudSpace', '$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $interval, $sce, CloudSpace, $ErrorResponseAlert) {

    	var cloudspaceupdater;
    	$scope.$watch('currentSpace.id + currentSpace.status',function(){
            if ($scope.currentSpace){
            	if ($scope.currentSpace.status != "DEPLOYED"){
            		if (!(angular.isDefined(cloudspaceupdater))){
            			cloudspaceupdater = $interval($scope.loadSpaces,5000);
            		}
            	}
            	else{
            		if (angular.isDefined(cloudspaceupdater)){
            			$interval.cancel(cloudspaceupdater);
            			cloudspaceupdater = undefined;
            		}
            	}
            }
        });
        
        $scope.$on(
                "$destroy",
                function( event ) {
                	if (angular.isDefined(cloudspaceupdater)){
                		$interval.cancel(cloudspaceupdater );
                		cloudspaceupdater = undefined;
                	}
                }
            );

    	
    	
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
