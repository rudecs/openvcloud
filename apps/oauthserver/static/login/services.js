'use strict';

angular.module('oauthserver').factory('loginService', [
  '$http',
  '$q',
  'api',
  '$log',
  function($http, $q, api, $log) {
    var self = {
      validateLogin: validateLogin,

      responses: {
        ok : 'ok',
        invalidPassword: 'invalid_password',
        tfaRequired: 'tfa_required',
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
             response !== self.responses.tfaRequired)
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

    return self;
  }
]);
