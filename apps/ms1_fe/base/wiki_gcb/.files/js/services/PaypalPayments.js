'use strict';

angular.module('cloudscalers.services')

.factory('PaypalPayments', function($http, $q) {
  return {
    initiatePayment: function(accountid, amount, currency) {

      return $http.get(cloudspaceconfig.apibaseurl +
        '/paypal/initiatepayment?accountId=' + encodeURIComponent(accountid) +
        '&amount=' + encodeURIComponent(amount) +
        '&currency=' + encodeURIComponent(currency))
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
