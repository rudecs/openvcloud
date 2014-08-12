angular.module('cloudscalers.controllers')
    .controller('ForgotPasswordController', ['$scope', 'Users', '$window', function($scope, Users, $window) {
        $scope.resetpasswordinput = {emailAddress : ''};
        $scope.resetpasswordresult = {succeeded:undefined, error:undefined};

        $scope.sendResetPasswordLink = function()
        {
        	$scope.resetpasswordresult.succeeded = undefined;
        	$scope.resetpasswordresult.error=undefined;
        	
        	Users.sendResetPasswordLink($scope.resetpasswordinput.emailAddress).then(
        			function(result){
        				$scope.resetpasswordresult.succeeded = true;
        			},
        			function(reason){
        					$scope.resetpasswordresult.error = reason.status;
        			}
        	);
        };
        
    }]);
