'use strict';

angular.module('oauthserver').controller('LoginPageController', [
  '$scope',
  'loginService',
  '$log',
  function($scope, loginService, $log) {
    $scope.needsTwoFactorAuthentication = false;
    $scope.login = "";
    $scope.password = "";
    $scope.securityCode = "";
    $scope.formErrors = {};

    $scope.loginChanged = function() {
      $scope.securityCode = "";
      $scope.needsTwoFactorAuthentication = false;
    };

    $scope.passwordChanged = function() {
      $scope.securityCode = "";
      $scope.needsTwoFactorAuthentication = false;
    };

    $scope.securityCodeChanged = function() {
      validate();
    };

    $scope.next = function() {
      if(!validate()) {
        return;
      }

      loginService
        .validatePasswordAndLogin($scope.login, $scope.password)
        .then(function(response) {
          if(response === loginService.responses.ok) {
            $log.debug('OK');

          } else if(response === loginService.responses.tfaRequired) {
            $scope.needsTwoFactorAuthentication = true;
            validate();

          } else {
            $log.debug('Invalid');
            $scope.formErrors.password = 'invalid';
          }
        });
    };

    function validate() {
      var flag = true;
      $scope.formErrors.login = null;
      $scope.formErrors.password = null;
      $scope.formErrors.securityCode = null;

      if(!$scope.login) {
        $scope.formErrors.login = 'required';
        flag = false;
      }

      if(!$scope.password) {
        $scope.formErrors.password = 'required';
        flag = false;
      }

      if($scope.needsTwoFactorAuthentication) {
        if(!$scope.securityCode || $scope.securityCode.length !== 6) {
          $scope.formErrors.securityCode = 'required';
          flag = false;
        }
      }

      return flag;
    }
  }
]);
