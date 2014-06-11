angular.module('cloudscalers.controllers')
    .controller('UserController', ['$scope', 'User', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, User, LoadingDialog, $ErrorResponseAlert, $timeout) {

        $scope.updatePassword = function() {
      		$scope.updateResultMessage = "";
      		if($scope.newPassword == $scope.retypePassword){
				LoadingDialog.show();
		      	User.updatePassword($scope.$parent.currentUser.username, $scope.oldPassword ,$scope.newPassword).then(
		        	function(passwordResponse){
		        		var passwordResponseCode = passwordResponse.data[0];
		        		var passwordResponseMsg = passwordResponse.data[1];
						if(passwordResponseCode == 203){
							LoadingDialog.hide();
							$scope.currentPasswordMessage = passwordResponseMsg;
							$timeout(function() {
	                            $scope.currentPasswordMessage = "";
	                        }, 3000);
						}
						if(passwordResponseCode == 200){
							LoadingDialog.hide();
							$scope.alertStatus = "success";
							$scope.updateResultMessage = passwordResponseMsg;
							$timeout(function() {
	                            $scope.updateResultMessage = "";
	                        }, 3000);
	                        $scope.oldPassword = "";
	                        $scope.newPassword = "";
	                        $scope.retypePassword = "";
						}
						if(passwordResponseCode == 400){
							LoadingDialog.hide();
							$scope.alertStatus = "error";
							$scope.updateResultMessage = passwordResponseMsg;
						}
					},
			        function(reason){
			          	$ErrorResponseAlert(reason.data);
			        }
			    );
	      	}else{
	      		$scope.newPasswordMessage = "Your new password dosen't match.";
				$timeout(function() {
                    $scope.newPasswordMessage = "";
                }, 3000);
	      	}
       }
    }]);
