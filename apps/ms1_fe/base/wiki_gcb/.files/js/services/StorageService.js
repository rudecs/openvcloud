
angular.module('cloudscalers.services')
	 .factory('StorageService',function ($http, $q) {
    	return {
    		getS3info: function(cloudSpaceId){
    			return $http.get(cloudspaceconfig.apibaseurl + '/s3storage/get?cloudspaceId=' + cloudSpaceId).then(
    					function(result){
    						return result.data;
    					},
    					function(reason){
    						return $q.reject(reason);
    					}
    					);
    		},
    		listS3Buckets: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/s3storage/listbuckets?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            }
        };
    });
