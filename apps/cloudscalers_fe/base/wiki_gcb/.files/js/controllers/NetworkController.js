
angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope', 'NetworkBuckets', '$modal',
    	function ($scope, NetworkBuckets, $modal) {
            $scope.$watch('currentSpace.id',function(){
	    		if ($scope.currentSpace){
	    			$scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
	    		}
    		});           
        }
    ]);