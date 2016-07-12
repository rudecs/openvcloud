'use strict';

angular.module('cloudscalers.services')
.factory('CryptoPayments', function($http, $q) {
  return {
    getPaymentInfo: function(accountid, coin) {
      var data = {accountId: accountId, count:coin};
      return $http.post(cloudspaceconfig.apibaseurl + '/payments/getPaymentInfo', data)
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
