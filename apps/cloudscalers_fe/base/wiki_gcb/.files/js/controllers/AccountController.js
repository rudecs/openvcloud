angular.module('cloudscalers.controllers')
    .controller('AccountController', ['$scope', 'Account', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, Account, LoadingDialog, $ErrorResponseAlert, $timeout) {
      	$scope.$parent.$watch('currentAccount', function(){
	      	$scope.accountNames = $scope.$parent.currentAccount.name;
	      	$scope.preferredDataLocation = $scope.$parent.currentAccount.preferredDataLocation;
	    });


        $scope.updatePassword = function() {
      		$scope.updateResultMessage = "";
      		if($scope.newPassword == $scope.retypePassword){
				LoadingDialog.show();
		      	Account.updatePassword($scope.$parent.currentUser.username, $scope.oldPassword ,$scope.newPassword).then(
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
