angular.module('cloudscalers.services')
     .factory('NetworkBuckets',function ($http, $q) {
        return {
            listPortforwarding: function() {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list').then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
            createPortforward: function(ip, puplicPort, vmName, localPort) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/create?ip=' + encodeURIComponent(ip) + "&puplicPort=" +
                    encodeURIComponent(puplicPort) + "&vmName=" + encodeURIComponent(vmName) + "&localPort=" + 
                    encodeURIComponent(localPort)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
            commonports: function() {
                return $http.get(cloudspaceconfig.apibaseurl + '/commonports/list').then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
        };
    });