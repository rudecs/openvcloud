'use strict';

angular.module('oauthserver').controller('LoginPageController', [
  '$scope',
  '$window',
  'loginService',
  '$log',
  function($scope, $window, loginService, $log) {
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
        .validateLogin($scope.login, $scope.password, $scope.securityCode)
        .then(function(response) {
          if(response === loginService.responses.ok) {
            $log.debug('OK');
            loginService
              .validateOauth($scope.login, $scope.password, $scope.securityCode)
              .then(function(url) {
                $window.location.href = url;
              });

          } else if(response === loginService.responses.invalidSecurityCode) {
            if(!$scope.needsTwoFactorAuthentication) {
              $scope.needsTwoFactorAuthentication = true;
              validate();
            } else {
              $scope.formErrors.securityCode = 'invalid';
            }

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
