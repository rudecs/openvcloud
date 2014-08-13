angular.module('cloudscalers.controllers')
    .controller('ResetPasswordController', ['$scope', 'Users','$window', '$timeout', function($scope, Users, $window, $timeout) {

    	$scope.verificationStatus = 'PENDING';

    	var uri = new URI($window.location);
    	var queryparams = URI.parseQuery(uri.query());
    	var resettoken = queryparams.token;

    	Users.getResetPasswordInformation(resettoken).then(function(result){

    		$scope.verificationStatus = 'VALIDTOKEN';
    		$scope.username = result.username;
    	}, function(reason){
    		if (reason.status == 419){
    			$scope.verificationStatus = 'EXPIRED';
    		}
    		else {
    			$scope.verificationStatus = 'ERROR';
    		}
    	});

    	  $scope.updatePassword = function() {
        		$scope.updateResultMessage = "";
        		$scope.alertStatus = undefined;
        		if($scope.newPassword != $scope.retypePassword){
  	      			$scope.alertStatus = "error";
  	      			$scope.updateResultMessage = "The given passwords do not match.";
  	      			return;
  	      		}
        		Users.resetPassword(resettoken,$scope.newPassword).then(
      				function(result){
      					$scope.verificationStatus = 'SUCCEEDED';
      					$scope.user.username = $scope.username;
      					$scope.user.password = $scope.newPassword;
      		    		$timeout(function(){
      		    			$scope.login();
      		    		}, 4000);
      				},
      				function(reason){
      					if (reason.status == 409){
      						$scope.alertStatus = "error";
      	  	      			$scope.updateResultMessage = reason.data;
      					}
      					else if (reason.status == 419){
      						$scope.verificationStatus = 'EXPIRED';
      					}
      					else {
      						$scope.verificationStatus = 'ERROR';
      					}
      				}
  		      	);
         }
    	
    }]);
