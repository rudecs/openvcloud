angular.module('cloudscalers.controllers')
    .controller('AccountController', ['$scope', 'Account', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, Account, LoadingDialog, $ErrorResponseAlert, $timeout) {
      	$scope.$parent.$watch('currentAccount', function(){
	      	$scope.accountNames = $scope.$parent.currentAccount.name;
	      	$scope.preferredDataLocation = $scope.$parent.currentAccount.preferredDataLocation;
	    });
    }]);
