angular.module('cloudscalers.controllers')
    .controller('AccountActivationController', ['$scope', 'User','$window', '$timeout', function($scope, User, $window, $timeout) {

    	$scope.verificationStatus = 'PENDING';

    	var uri = new URI($window.location);
    	queryparams = URI.parseQuery(uri.query());
    	activationtoken = queryparams.activationtoken;

    	User.activateAccount(activationtoken).then(function(result){

    		$scope.verificationStatus = 'ACCEPTED';
    		$timeout(function(){
    			var uri = new URI($window.location);
                uri.filename('Login');
                $window.location = uri.toString();
    		}, 5000);
    	}, function(reason){
    		if (reason.status == 419){
    			$scope.verificationStatus = 'EXPIRED';
    		}
    		else {
    			$scope.verificationStatus = 'ERROR';
    		}
    	});

    }]);
