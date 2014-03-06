angular.module('cloudscalers.controllers')
    .controller('NetworkController', ['$scope',
        function ($scope) {
            $scope.$watch('currentSpace.id',function(){
    		if ($scope.currentSpace){
    			$scope.managementui = "http://" + $scope.currentSpace.publicipaddress
    		}
    	});
        }
    ]);