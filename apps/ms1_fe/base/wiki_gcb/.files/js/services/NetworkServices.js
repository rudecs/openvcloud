angular.module('cloudscalers.services')
     .factory('Networks',function ($http, $q) {
        return {
            listPortforwarding: function(id, machineId) {
                if(encodeURIComponent(id) == "undefined"){
                    return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list').then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
                }
                else{
                    if(machineId){
                        return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list?cloudspaceid=' + encodeURIComponent(id) + '&machineId=' + encodeURIComponent(machineId)).then(
                            function(result){
                                return result.data;
                            },
                            function(reason){
                                return $q.reject(reason);
                            }
                        );
                    }else{
                        return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/list?cloudspaceid=' + encodeURIComponent(id)).then(
                            function(result){
                                return result.data;
                            },
                            function(reason){
                                return $q.reject(reason);
                            }
                        );
                    }
                }

            },
            createPortforward: function(id, ip, publicPort, vmid, localPort, protocol) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/create?cloudspaceid=' + encodeURIComponent(id) + '&publicIp=' + encodeURIComponent(ip) + "&publicPort="+ encodeURIComponent(publicPort) + "&vmid=" + encodeURIComponent(vmid) + "&localPort=" +
                    encodeURIComponent(localPort) + '&protocol=' + encodeURIComponent(protocol)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            },
            updatePortforward: function(cloudspaceid, id, ip, publicPort, vmid, localPort, protocol) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/update?cloudspaceid=' + encodeURIComponent(cloudspaceid) + '&id=' + encodeURIComponent(id) + "&publicIp=" + encodeURIComponent(ip) + "&publicPort=" + encodeURIComponent(publicPort) + "&vmid=" +
                    encodeURIComponent(vmid) + "&localPort=" +encodeURIComponent(localPort) + '&protocol=' + encodeURIComponent(protocol)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            },
            deletePortforward: function(cloudspaceid, id) {
                return $http.get(cloudspaceconfig.apibaseurl + '/portforwarding/delete?cloudspaceid=' + encodeURIComponent(cloudspaceid) + '&id=' + encodeURIComponent(id)).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            },
            commonports: function() {
               return [
                    {port: '80', name: 'HTTP'},
                    {port: '443', name: 'HTTPS'},
                    {port: '21', name: 'FTP'},
                    {port: '22', name: 'SSH'},
                    {port: '3389', name: 'RDP'}
                ];
            },
        };
    });
