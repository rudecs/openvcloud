(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('RegisterUserController', RegisterUserController);

  function RegisterUserController($scope, Users, $window, $timeout) {
    $scope.verificationStatus = 'PENDING';

    var uri = new URI($window.location);
    var queryparams = URI.parseQuery(uri.query());
    $scope.registerToken = queryparams.token;
    $scope.registerEmail = queryparams.email;
    $scope.registerInvitedUser = registerInvitedUser;

    // Initialization: Functions invokation logic
    checkUserInviteValidty();

    // Functions
    function checkUserInviteValidty() {
      Users.isValidInviteUserToken($scope.registerToken, $scope.registerEmail)
      .then(function() {
        $scope.isValidToken = true;
        $scope.verificationStatus = '';
      }, function(reason) {
        $scope.isValidToken = false;
        $scope.verificationStatus = 'ERROR';
        $scope.verificationMessage = JSON.parse(reason.data);
      });
    }

    function registerInvitedUser() {
      $scope.updateResultMessage = '';
      $scope.alertStatus = undefined;
      if ($scope.newPassword !== $scope.retypePassword) {
        $scope.alertStatus = 'error';
        $scope.updateResultMessage = 'The given passwords do not match.';
        return;
      }
      Users.registerInvitedUser($scope.registerToken,$scope.registerEmail,
        $scope.registerUsername, $scope.registerNewPassword, $scope.registerRetypePassword)
      .then(
        function() {
          $scope.verificationStatus = 'SUCCEEDED';
          $scope.user.username = $scope.registerUsername;
          $scope.user.password = $scope.registerNewPassword;
          $timeout(function() {
            $scope.login();
          }, 2000);
        },
        function(reason) {
          $scope.verificationStatus = 'ERROR';
          $scope.verificationMessage = JSON.parse(reason.data);
        }
      );
    }
  }
})();
