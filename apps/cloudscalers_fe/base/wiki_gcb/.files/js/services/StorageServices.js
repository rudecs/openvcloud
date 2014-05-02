
angular.module('cloudscalers.services')
	 .factory('Storagebuckets',function ($http, $q) {
    	return {
    		getS3info: function(cloudSpaceId){
    			return $http.get(cloudspaceconfig.apibaseurl + '/s3storage/get?cloudspaceId=' + cloudSpaceId).then(
    					function(result){
    						return result.data;
    					},
    					function(reason){
    						return $q.defer(reason);
    					}
    					);
    		},
    		listS3Buckets: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/s3storage/listbuckets?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.defer(reason);
                        }
                    );
            }
        };
    });