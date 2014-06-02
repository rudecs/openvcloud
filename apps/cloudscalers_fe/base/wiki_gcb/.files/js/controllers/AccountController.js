angular.module('cloudscalers.controllers')
    .controller('AccountController', ['$scope', 'Account', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, Account, LoadingDialog, $ErrorResponseAlert, $timeout) {
      	$scope.$parent.$watch('currentAccount', function(){
	      	// console.log($scope);
	      	$scope.accountNames = $scope.$parent.currentAccount.name;
	      	$scope.preferredDataLocation = $scope.$parent.currentAccount.preferredDataLocation;
	    });


      	$scope.updatePassword = function() {
      		if($scope.newPassword == $scope.retypePassword){
				LoadingDialog.show();
		      	Account.updatePassword($scope.$parent.currentUser.username, $scope.oldPassword ,$scope.newPassword).then(
		        	function(code){
						if(code == 203){
							LoadingDialog.hide();
							$scope.currentPasswordMessage = "Your current password dosen't match!";
							console.log($scope.currentPasswordMessage);
							$timeout(function() {
	                            $scope.currentPasswordMessage = "";
	                        }, 3000);
						}
						if(code == 200){
							LoadingDialog.hide();
							$scope.updateResultMessage = "Congratulations, Your password changed successfully.";
							$timeout(function() {
	                            $scope.updateResultMessage = "";
	                        }, 3000);
	                        $scope.oldPassword = "";
	                        $scope.newPassword = "";
	                        $scope.retypePassword = "";
						}
					},
			        function(reason){
			          	$ErrorResponseAlert(reason);
			          	console.log(reason);
			        }
			    );
	      	}else{
	      		$scope.newPasswordMessage = "New password fileds dosen't match!";
				$timeout(function() {
                    $scope.newPasswordMessage = "";
                }, 3000);
	      	}
       }
    }]);