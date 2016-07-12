'use strict';

angular.module('cloudscalers.services')

.factory('PaypalPayments', function($http, $q) {
  return {
    initiatePayment: function(accountid, amount, currency) {
      var data = {accountId: accountid, amount: amount, currency: currency};
      return $http.post(cloudspaceconfig.apibaseurl + '/paypal/initiatepayment', data)
      .then(
        function(result) {
          var info = {'paypalurl': result.data.paypalurl};
          return info;
        },function(reason) {
          return $q.reject(reason);
        }
      );
    }
  };
});
