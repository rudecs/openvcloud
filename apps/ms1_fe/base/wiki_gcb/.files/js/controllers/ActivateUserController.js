(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('ActivateUserController', ActivateUserController);

  function ActivateUserController($scope, Users) {
    $scope.activateUserFunc = activateUserFunc;

    function getUrlParameter(sParam) {
      var sPageURL = decodeURIComponent(window.location.search.substring(1));
      var sURLVariables = sPageURL.split('&');
      var sParameterName;
      var i;

      for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
          return sParameterName[1] === undefined ? true : sParameterName[1];
        }
      }
    }
    function activateUserFunc() {
      $scope.activateUser.error = '';
      if ($scope.activateUser.password.length < 8) {
        $scope.activateUser.error = 'Password should be at least 8 characters.';
        return;
      }
      if ($scope.activateUser.password === $scope.activateUser.confirmPassword) {
        Users.activateUser(getUrlParameter('token'), $scope.activateUser.password).then(
          function() {
            window.location.pathname = '/restmachine/system/oauth/authenticate';
          }, activeUserError);
      }else {
        activeUserError('Entered passwords should be the same.');
      }
    }
    function activeUserError(reason) {
      $scope.activateUser.error = reason.data;
    }
  }
})();
