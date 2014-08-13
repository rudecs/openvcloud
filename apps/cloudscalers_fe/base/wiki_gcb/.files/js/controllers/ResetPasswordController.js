angular.module('cloudscalers.controllers')
    .controller('ResetPasswordController', ['$scope', 'Users','$window', '$timeout', function($scope, Users, $window, $timeout) {

    	$scope.verificationStatus = 'PENDING';

    	var uri = new URI($window.location);
    	queryparams = URI.parseQuery(uri.query());
    	resettoken = queryparams.token;

    	Users.getResetPasswordInformation(resettoken).then(function(result){

    		$scope.verificationStatus = 'VALIDTOKEN';
//    		$timeout(function(){
//    			var uri = new URI($window.location);
//                uri.filename('Login');
//                $window.location = uri.toString();
//    		}, 5000);
    	}, function(reason){
    		if (reason.status == 419){
    			$scope.verificationStatus = 'EXPIRED';
    		}
    		else {
    			$scope.verificationStatus = 'ERROR';
    		}
    	});

    }]);
