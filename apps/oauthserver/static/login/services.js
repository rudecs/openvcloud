'use strict';

angular.module('oauthserver').factory('loginService', [
  '$http',
  '$q',
  'api',
  '$log',
  function($http, $q, api, $log) {
    var self = {
      validatePasswordAndLogin: validatePasswordAndLogin,

      responses: {
        ok : 'ok',
        invalid: 'invalid',
        tfaRequired: 'tfa_required',
      },
    };

    function validatePasswordAndLogin(login, password) {
      var d = $q.defer();

      var request = {
        'login': login,
        'password': password,
      };

      $log.debug('request:', request);

      $http
        .post(api.resource('/validate_login_password'), request)
        .then(function(result) {
          var response = result.data.status;
          if(response !== self.responses.ok &&
             response !== self.responses.invalid &&
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
