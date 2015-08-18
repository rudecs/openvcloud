'use strict';

angular.module('oauthserver').factory('api', [
  function() {
    var self = {
      baseURL: '/api',

      resource: resource,
    };

    function resource(path) {
      return self.baseURL + path;
    }

    return self;
  }
]);
