'use strict';

angular.module('oauthserver').factory('loginService', [
  '$http',
  '$q',
  '$location',
  'api',
  '$log',
  function($http, $q, $location, api, $log) {
    var self = {
      validateLogin: validateLogin,
      validateOauth: validateOauth,

      responses: {
        ok : 'ok',
        invalidPassword: 'invalid_password',
        invalidSecurityCode: 'invalid_security_code',
      },
    };

    function validateLogin(login, password, securityCode) {
      var d = $q.defer();

      var request = {
        'login': login,
        'password': password,
        'securityCode': securityCode,
      };

      $log.debug('request:', request);

      $http
        .post(api.resource('/login/validate'), request)
        .then(function(result) {
          var response = result.data.status;
          if(response !== self.responses.ok &&
             response !== self.responses.invalidPassword &&
             response !== self.responses.invalidSecurityCode)
          {
            $log.error('error: unknown response:', response);
            return;
          }

          d.resolve(response);

        }, function(result) {
          $log.error('error:', result);
        });

      return d.promise;
    }

    function validateOauth(login, password, securityCode) {
      var d = $q.defer();

      var query = $location.search();

      var request = {
        'client_id': query.client_id,
        'redirect_url': query.redirect_url,
        'response_type': query.response_type,
        'scope': query.scope,
        'state': query.state,

        'login': login,
        'password': password,
        'securityCode': securityCode,
      };

      $http({
        method: 'POST',
        url: api.resource('/oauth/validate'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        transformRequest: function(obj) {
          var str = [];
          $log.debug('converting:', obj);
          for(var p in obj) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
          }
          $log.debug('to:', str.join('&'));
          return str.join("&");
        },
        data: request,
      })
        .then(function(result) {
          var data = result.data;
          if(data.action === 'redirect') {
            d.resolve(data.url);
          } else {
            $log.error('error: unknown action:', data.action);
          }
        }, function(result) {
          $log.debug('error:', result);
        });

      return d.promise;
    }

    return self;
  }
]);
