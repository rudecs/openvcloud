'use strict';

angular.module('oauthserver', [
  'ngRoute',
]);

angular.module('oauthserver').config([
  '$routeProvider',
  function($routeProvider) {
    $routeProvider
      .when('/login/oauth/authorize', {
        templateUrl: 'login/login.html',
      });
  }
]);
