'use strict';

angular.module('cloudscalers.services')
.factory('LocationsService', function($http, $q) {
  // var locations = {
  //   'ca1': {title: 'Canada', flag: 'canada'},
  //   'us1': {title: 'United States', flag: 'usa'},
  //   'uk1': {title: 'United Kingdom', flag: 'uk'},
  //   'be1': {title: 'Belgium', flag: 'belgium'},
  //   'test1': {title: 'Test', flag: 'black'}
  // };
  return {
    list: function() {
      return $http.get(cloudspaceconfig.apibaseurl + '/locations/list').then(
        function(result) {
          return result.data;
        },
        function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
});
