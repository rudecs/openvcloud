angular.module('cloudscalers.controllers')
    .controller('UsersController', ['$scope', 'Users', 'LoadingDialog','$ErrorResponseAlert', '$timeout',
    	function($scope, Users, LoadingDialog, $ErrorResponseAlert, $timeout) {

        $scope.updatePassword = function() {
      		$scope.updateResultMessage = "";
      		if($scope.newPassword == $scope.retypePassword){
				LoadingDialog.show();
		      	Users.updatePassword($scope.$parent.currentUser.username, $scope.oldPassword ,$scope.newPassword).then(
		        	function(passwordResponse){
		        		var passwordResponseCode = passwordResponse.data[0];
		        		var passwordResponseMsg = passwordResponse.data[1];
						if(passwordResponseCode == 200){
							LoadingDialog.hide();
							$scope.alertStatus = "success";
							$scope.updateResultMessage = passwordResponseMsg;

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
			$scope.alertStatus = "error";
	      		$scope.updateResultMessage = "The given passwords do not match.";
	      	}
       }
    }]);
