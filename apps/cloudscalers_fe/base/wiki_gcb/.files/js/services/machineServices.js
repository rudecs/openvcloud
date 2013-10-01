angular.module('cloudscalers.machineServices', ['ng'])

	.factory('authenticationInterceptor',['$q','$log','User',function($q, $log, User){
	  return {
	   'request': function(config) {
		   if (config) {
			  url = config.url;
			  
			  if(/\/machines\//i.test(url) || /\/sizes\//i.test(url) || /\/images\//i.test(url)) {
				  
				   uri = new URI(url);
				   uri.addSearch('api_key',User.get_api_key());
				   config.url = uri.toString();
				}
		   }
		   return config || $q.when(config);
	    },
	    'response': function(response) {
	    	$log.log("Response intercepted");
	       return response || $q.when(response);
	    }
	  };
	 }])
	 .config(['$httpProvider',function($httpProvider) {
		 $httpProvider.interceptors.push('authenticationInterceptor');
	 }])
    .factory('User', function ($window) {
        var user = {};
        user.login = function () {
            var loginResult = {
            };
//            $http({
//                method: 'POST',
//                data: {
//                    username: username,
//                    password: password
//                },
//                url: cloudspaceconfig.apibaseurl + '/users/authenticate'
//            }).
//            success(function (data, status, headers, config) {
//                loginResult.api_key = data;
//            }).
//            error(function (data, status, headers, config) {
//                loginResult.error = status;
//            });
            return loginResult;
        };
        
        user.get_api_key = function(){
        	return 'yep123456789';
        }
        
        
        return user;
    })
    .factory('Machine', function ($http, $sce) {
        return {
            action: function (machineid, action) {
                var result = []
                url = cloudspaceconfig.apibaseurl + '/machines/action?machineId=' + machineid + '&action=' + action;
                $http.get(url)
                    .success(function (data, status, headers, config) {
                        result.success = true;
                    }).error(function (data, status, headers, config) {
                        result.error = status;
                    });
                return result;
            },
            create: function (cloudspaceid, name, description, sizeId, imageId) {
                var machine = [];
                url = cloudspaceconfig.apibaseurl + '/machines/create?cloudspaceId=' + cloudspaceid + '&name=' + name + '&description=' + description + '&sizeId=' + sizeId + '&imageId=' + imageId;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        machine.id = data;
                    }).error(function (data, status, headers, config) {
                    machine.error = status;
                });
                return machine;
            },
            delete: function (machineid) {
                var result = []
                url = cloudspaceconfig.apibaseurl + '/machines/delete?machineId=' + machineid;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        result.success = true;
                    }).error(function (data, status, heades, config) {
                    result.error = status;
                });
                return result;
            },
            list: function (cloudspaceid) {
                var machines = [];
                url = cloudspaceconfig.apibaseurl + '/machines/list?cloudspaceId=' + cloudspaceid + '&type=';
                $http.get(url).success(
                    function (data, status, headers, config) {
                        _.each(data, function (machine) {
                            machines.push(machine);
                        });
                    }).error(
                    function (data, status, headers, config) {
                        machines.error = status;
                    });
                return machines;
            },
            get: function (machineid) {
                var machine = {
                    id: machineid
                };
                url = cloudspaceconfig.apibaseurl + '/machines/get?machineId=' + machineid;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        angular.copy(data, machine);
                    }).error(
                    function (data, status, headers, config) {
                        machine.error = status;
                    });
                return machine;
            },
            listSnapshots: function (machineid) {
                var snapshotsResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/listSnapshots?machineId=' + machineid;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        snapshotsResult.snapshots = data;
                    }).error(
                    function (data, status, headers, config) {
                        snapshotsResult.error = status;
                    });
                return snapshotsResult;
            },
            createSnapshot: function (machineId, snapshotName) {
                var createSnapshotResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/snapshot?machineId=' + machineId + '&snapshotName=' + snapshotName;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        createSnapshotResult.success = true;
                    }).error(
                    function (data, status, headers, config) {
                        createSnapshotResult.error = status;
                    });
                return createSnapshotResult;
            },
            getConsoleUrl: function(machineId) {
                var getConsoleUrlResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/getConsoleUrl?machineId=' + machineId;
                $http.get(url).success(function(data, status, headers, config) {
                    if (data == 'None') {
                        getConsoleUrlResult.error = status;
                    } else {
                        getConsoleUrlResult.url = $sce.trustAsResourceUrl(data);
                    }
                }).error(function (data, status, headers, config) {
                    getConsoleUrlResult.error = status;
                });
                return getConsoleUrlResult;
            }
        }
    })
    .factory('Image', function ($http) {
        return {
            list: function () {
                var images = [];
                url = cloudspaceconfig.apibaseurl + '/images/list';
                $http.get(url).success(
                    function (data, status, headers, config) {
                        _.each(data, function (img) {
                            images.push(img);
                        });
                    }).error(
                    function (data, status, headers, config) {
                        images.error = status;
                    });
                return images;
            }
        }
    })
    .factory('Size', function ($http) {
        return {
            list: function () {
                var sizes = [];
                url = cloudspaceconfig.apibaseurl + '/sizes/list';
                $http.get(url).success(
                    function (data, status, headers, config) {
                        _.each(data, function (size) {
                            sizes.push(size);
                        });
                    }).error(
                    function (data, status, headers, config) {
                        sizes.error = status;
                    });
                return sizes;
            }
        }
    });
