angular.module('cloudscalers.controllers')
    .controller('ForgotPasswordController', ['$scope', 'User', '$window', function($scope, User, $window) {
        $scope.resetpasswordinput = {emailAddress : ''};
        $scope.resetpasswordresult = {succeeded:undefined};

        $scope.sendResetPasswordLink = function()
        {
        	return;
        };
        
    }]);
