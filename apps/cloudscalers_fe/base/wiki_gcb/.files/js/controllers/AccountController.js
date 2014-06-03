angular.module('cloudscalers.controllers')
    .controller('AccountController', ['$scope', 'Account', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, Account, LoadingDialog, $ErrorResponseAlert, $timeout) {
    	$scope
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
						if(passwordResponse.status == 203){
							LoadingDialog.hide();
							$scope.currentPasswordMessage = passwordResponse.data;
							console.log($scope.currentPasswordMessage);
							$timeout(function() {
	                            $scope.currentPasswordMessage = "";
	                        }, 3000);
						}
						if(passwordResponse.status == 200){
							LoadingDialog.hide();
							$scope.alertStatus = "success";
							$scope.updateResultMessage = passwordResponse.data;
							$timeout(function() {
	                            $scope.updateResultMessage = "";
	                        }, 3000);
	                        $scope.oldPassword = "";
	                        $scope.newPassword = "";
	                        $scope.retypePassword = "";
						}
					},
			        function(reason){
			        	if(reason.status == 400){
							LoadingDialog.hide();
							$scope.alertStatus = "error";
							$scope.updateResultMessage = reason.data;
						}else{
			          		$ErrorResponseAlert(reason.data);
						}
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