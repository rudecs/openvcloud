angular.module('cloudscalers.controllers')
    .controller('SessionController', ['$scope', 'User', '$window', '$timeout', function($scope, User, $window, $timeout) {
        $scope.user = {username : '', password:''};

        $scope.login_error = undefined;

        $scope.login = function() {
            $scope.$broadcast("autofill:update");
        	var usertologin = $scope.user.username;
            User.login(usertologin, $scope.user.password).
            then(
            		function(result) {
            			$scope.login_error = undefined;
            			User.updateUserDetails(usertologin).then(
                                function(result) {
                        			var uri = new URI($window.location);
                        			uri.filename('Decks');
                        			$window.location = uri.toString();
                                },
                                function(reason){
                                	$scope.login_error = reason.status
                                });
            		},
            		function(reason) {
            			$scope.login_error = reason.status;
            		}
            );
        };
        $scope.waitlogin = function() {
            $scope.$broadcast("autofill:update");
            var usertologin = $scope.user.username;
            User.waitlogin(usertologin, $scope.user.password).
            then(
                    function(result) {
                        $scope.login_error = undefined;
                        var uri = new URI($window.location);
                        uri.filename('SignUpValidation');
                        $window.location = uri.toString();
                        $scope.user.password = "";
                        $scope.passwordConfirmation = "";
                    },
                    function(reason) {
                        $scope.login_error = reason.status;
                    }
            );
        };
        $timeout(function() {
            // Read the value set by browser autofill
            $scope.user.username = angular.element('[ng-model="user.username"]').val();
            $scope.user.password =angular.element('[ng-model="user.password"]').val();
        }, 0);
    }]).directive("autofill", function () {
    return {
        require: "ngModel",
        link: function (scope, element, attrs, ngModel) {
            scope.$on("autofill:update", function() {
                ngModel.$setViewValue(element.val());
            });
        }
    }
});;
