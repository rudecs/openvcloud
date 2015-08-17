'use strict';

angular.module('oauthserver', [
  'ngRoute',
  'ngMaterial',
]);

angular.module('oauthserver').config([
  '$routeProvider',
  '$mdThemingProvider',
  function($routeProvider, $mdThemingProvider) {
    $routeProvider
      .when('/login/oauth/authorize', {
        templateUrl: 'login/login.html',
      });

    $mdThemingProvider.theme('default')
      .primaryPalette('grey');
  }
]);
