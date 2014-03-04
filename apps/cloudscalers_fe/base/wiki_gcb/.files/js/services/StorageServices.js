
angular.module('cloudscalers.services')
	 .factory('Storagebuckets',function ($http, $q) {
    	return {
            listStorgaesByCloudSpace: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/storagebuckets/list?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            }
        };
    });