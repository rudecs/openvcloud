(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers', ['ngCookies'])
    .controller('SessionController', SessionController).directive('autofill', autofill);

  function SessionController($scope, User, $window, $timeout, $location, SessionData, $cookies) {
    $scope.user = {username: '', password: '', company: '', vat: ''};

    $scope.loginError = undefined;
    SessionData.setUser({username: '', api_key: '', tourTips: ''});

    var portalSessionCookie = $cookies['beaker.session.id'];
    if (portalSessionCookie) {
      User.getPortalLoggedinUser().then(function(username) {
        if (username !== 'guest') {
          User.portalLogin(username, portalSessionCookie);
          var target = 'Decks';
          var uri = new URI($window.location);
          uri.filename(target);
          $window.location = uri.toString();
        }
      },function(reason) {
        $scope.loginError = reason.status;
      });
    }

    $scope.login = function() {
      $scope.$broadcast('autofill:update');
      var usertologin = $scope.user.username;
      User.login(usertologin, $scope.user.password).
      then(
        function() {
          $scope.loginError = undefined;
          User.updateUserDetails(usertologin).then(
            function(result) {
              var target = 'Decks';
              if (result.status === 409) {
                target = 'AccountValidation';
              }
              var uri = new URI($window.location);
              uri.filename(target);
              $window.location = uri.toString();
            },
            function(reason) {
              $scope.loginError = reason.status;
            }
          );
        },
        function(reason) {
          $scope.loginError = reason.status;
        }
      );
    };

    if ($location.search().username && $location.search().apiKey) {
      SessionData.setUser({username: $location.search().username, api_key: $location.search().apiKey});
      var target = 'Decks';
      var uri = new URI($window.location);
      uri.filename(target);
      uri.query('');
      $window.location = uri.toString();
    }
    $timeout(function() {
      // Read the value set by browser autofill
      $scope.user.username = angular.element('[ng-model="user.username"]').val();
      $scope.user.password = angular.element('[ng-model="user.password"]').val();
    }, 0);
  }
  function autofill() {
    return {
      require: 'ngModel',
      link: function(scope, element, attrs, ngModel) {
        scope.$on('autofill:update', function() {
          ngModel.$setViewValue(element.val());
        });
      }
    };
  }
})();
