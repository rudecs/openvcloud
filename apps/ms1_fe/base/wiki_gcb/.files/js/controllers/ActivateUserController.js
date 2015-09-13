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
            console.log("You bastard!");
            if($scope.activateUser.password == $scope.activateUser.confirmPassword){
                $scope.activateUser.error = "";
                Users.activateUser(getUrlParameter('token'), $scope.activateUser.password).then(
                    function(result) {
                        var uri = new URI($window.location);
                        uri.filename('Decks');
                        $window.location = uri.toString();
                    },
                    function(reason) {
                        //$ErrorResponseAlert(reason);
                    }
                )
            }else{
                $scope.activateUser.error = "Entered passwords should be the same.";
            }
        };
        
    }]);
