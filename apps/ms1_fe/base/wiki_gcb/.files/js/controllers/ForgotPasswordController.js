(function() {
  'use strict';
  //jshint latedef: nofunc
  angular.module('cloudscalers.controllers')
  .controller('ForgotPasswordController', ForgotPasswordController);

  function ForgotPasswordController($scope, Users) {
    $scope.resetpasswordinput = {emailAddress: ''};
    $scope.resetpasswordresult = {succeeded: undefined, error: undefined};

    $scope.sendResetPasswordLink = function() {
      $scope.resetpasswordresult.succeeded = undefined;
      $scope.resetpasswordresult.error = undefined;

      Users.sendResetPasswordLink($scope.resetpasswordinput.emailAddress).then(
        function() {
          $scope.resetpasswordresult.succeeded = true;
        },function(reason) {
          $scope.resetpasswordresult.error = reason.status;
        }
      );
    };
  }
})();
