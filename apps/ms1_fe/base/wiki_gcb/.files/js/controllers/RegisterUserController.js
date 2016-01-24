angular.module('cloudscalers.controllers')
    .controller('RegisterUserController', ['$scope', 'Users','$window', '$timeout', function($scope, Users, $window, $timeout) {

    	$scope.verificationStatus = 'PENDING';

    	var uri = new URI($window.location);
    	var queryparams = URI.parseQuery(uri.query());
    	$scope.registerToken = queryparams.token;
      $scope.registerEmail = queryparams.email;

    	Users.isValidInviteUserToken($scope.registerToken, $scope.registerEmail).then(function(result){
    		$scope.verificationStatus = 'VALIDTOKEN';
    	}, function(reason){
    			$scope.verificationStatus = "ERROR";
          $scope.verificationMessage = reason.data;
    	});

    	  $scope.registerInvitedUser = function() {
        		$scope.updateResultMessage = "";
        		$scope.alertStatus = undefined;
        		if($scope.newPassword != $scope.retypePassword){
  	      			$scope.alertStatus = "error";
  	      			$scope.updateResultMessage = "The given passwords do not match.";
  	      			return;
  	      		}
        		Users.registerInvitedUser($scope.registerToken, $scope.registerEmail, $scope.registerUsername, $scope.registerNewPassword, $scope.registerRetypePassword).then(
      				function(result){
      					$scope.verificationStatus = 'SUCCEEDED';
      					$scope.user.username = $scope.registerUsername;
      					$scope.user.password = $scope.registerNewPassword;
      		    		$timeout(function(){
      		    			$scope.login();
      		    		}, 2000);
      				},
      				function(reason){
                $scope.verificationStatus = "ERROR";
                $scope.verificationMessage = reason.data;
      				}
  		      	);
         }

    }]);
