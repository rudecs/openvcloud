angular.module('cloudscalers.controllers')
    .controller('ActivateUserController', ['$scope', 'Users', '$location', '$window',function($scope, Users, $location, $window) {
        var getUrlParameter = function getUrlParameter(sParam) {
            var sPageURL = decodeURIComponent(window.location.search.substring(1)),
                sURLVariables = sPageURL.split('&'),
                sParameterName,
                i;

            for (i = 0; i < sURLVariables.length; i++) {
                sParameterName = sURLVariables[i].split('=');

                if (sParameterName[0] === sParam) {
                    return sParameterName[1] === undefined ? true : sParameterName[1];
                }
            }
        };

        $scope.activateUserFunc = function() {
            $scope.activateUser.error = "";
            if($scope.activateUser.password.length < 8){
                $scope.activateUser.error = "Password should be at least 8 characters."
                return;
            }
            if($scope.activateUser.password == $scope.activateUser.confirmPassword){
                Users.activateUser(getUrlParameter('token'), $scope.activateUser.password).then(
                    function(result) {
                        window.location.pathname = "/restmachine/system/oauth/authenticate";
                    },
                    function(reason) {
                        $scope.activateUser.error = reason.data;
                    }
                )
            }else{
                $scope.activateUser.error = "Entered passwords should be the same.";
            }
        };
        
    }]);
