
angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', '$modal',
    	function ($scope, $modal) {
            $scope.$watch('currentSpace.id',function(){
	    		if ($scope.currentSpace){
	    			$scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
	    		}
    		});           
        }
    ]);