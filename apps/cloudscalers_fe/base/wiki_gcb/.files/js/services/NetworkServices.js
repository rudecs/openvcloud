angular.module('cloudscalers.services')
     .factory('NetworkBuckets',function ($http, $q) {
        return {
            listPortforwarding: function(id) {
                if(encodeURIComponent(id) == "undefined"){
                    return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list').then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
                }
                else{
                    return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list?cloudspaceid=' + encodeURIComponent(id)).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
                }
                
            },
            createPortforward: function(ip, puplicPort, vmName, localPort) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/create?publicIp=' + encodeURIComponent(ip) + "&puplicPort=" +
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
            updatePortforward: function(id, ip, puplicPort, vmName, localPort) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/update?ip=' + encodeURIComponent(ip) + "&puplicPort=" +
                    encodeURIComponent(puplicPort) + "&vmName=" + encodeURIComponent(vmName) + "&localPort=" + 
                    encodeURIComponent(localPort) + "&id=" + encodeURIComponent(id)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
            deletePortforward: function(cloudspaceid, id) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/delete?cloudspaceid=' + encodeURIComponent(cloudspaceid) + '&id=' + encodeURIComponent(id)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
            commonports: function() {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/listcommonports').then(
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