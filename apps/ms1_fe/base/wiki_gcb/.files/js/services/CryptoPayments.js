'use strict';

angular.module('cloudscalers.services')
.factory('CryptoPayments', function($http, $q) {
  return {
    getPaymentInfo: function(accountid, coin) {
      return $http.get(cloudspaceconfig.apibaseurl +
        '/payments/getPaymentInfo?accountId=' + encodeURIComponent(accountid) +
        '&coin=' + encodeURIComponent(coin))
        .then(
          function(result) {
            var info = {'coin': coin};
            info.value = result.data.value;
            info.address = result.data.address;
            return info;
          }, function(reason) {
            return $q.reject(reason);
          }
        );
    }
  };
});
