angular.module('cloudscalers.machineServices', ['ng'])

	.factory('authenticationInterceptor',['$q','$log', 'APIKey', function($q, $log, APIKey){
        return {
            'request': function(config) {
                if (config) {
                    url = config.url;

                    if(/\/machines\//i.test(url) || /\/sizes\//i.test(url) || /\/images\//i.test(url)) {
                        uri = new URI(url);
                        uri.addSearch('api_key', APIKey.get());
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
    .factory('APIKey', function($window) {
        var clientApiKey;
        return {
            get: function() { 
                return $window.localStorage.getItem('gcb:api_key');
            },
            set: function(apiKey) {
                $window.localStorage.setItem('gcb:api_key', apiKey);
            },
            clear: function() {
                $window.localStorage.removeItem('gcb:api_key');
            }
        };
    })
    .factory('User', function ($window, $http, $rootScope, APIKey) {
        var user = {};
        user.login = function (username, password) {
            var loginResult = {api_key: undefined, error: false};
            $http({
                method: 'POST',
                data: {
                    username: username,
                    password: password
                },
                url: cloudspaceconfig.apibaseurl + '/users/authenticate'
            }).
            success(function (data, status, headers, config) {
                loginResult.api_key = data;
                APIKey.set(data);
                loginResult.error = false;
                $rootScope.$broadcast('event:login-successful', loginResult);
            }).
            error(function (data, status, headers, config) {
                loginResult.api_key = undefined;
                APIKey.set(undefined);
                loginResult.error = status;
                $rootScope.$broadcast('event:login-error', loginResult);
            });
            return loginResult;
        };

        user.logout = function() {
            APIKey.clear();
        };

        user.signUp = function(username, password) {
            var signUpResult = {};
            $http({
                method: 'POST',
                data: {
                    username: username,
                    password: password
                },
                url: cloudspaceconfig.apibaseurl + '/users/signup'
            })
            .success(function(data, status, headers, config) {
                signUpResult.success = true;
                $rootScope.$broadcast('event:signUp-successful', signUpResult);
            })
            .error(function(data, status, headers, config) {
                signUpResult.error = status;
                $rootScope.$broadcast('event:signUp-error', signUpResult);
            });
            return signUpResult;
        }
        
        return user;
    })
    .factory('Machine', function ($http, $sce) {
        $http.defaults.get = {'Content-Type': 'application/json', 'Accept': 'Content-Type: application/json'};
        return {
            action: function (machineid, action) {
                var result = []
                url = cloudspaceconfig.apibaseurl + '/machines/action?format=jsonraw&machineId=' + machineid + '&action=' + action;
                $http.get(url)
                    .success(function (data, status, headers, config) {
                        result.success = true;
                    }).error(function (data, status, headers, config) {
                        result.error = status;
                    });
                return result;
            },
            boot: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/boot?format=jsonraw&machineId=' + machine.id;
                $http.get(url)
                    .success(function(data, status, headers, config) {
                        machine.status = data;   
                    })
                    .error(function(data, status, headers, config) {
                    });
            },
            powerOff: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/poweroff?format=jsonraw&machineId=' + machine.id;
                $http.get(url)
                    .success(function(data, status, headers, config) {
                        machine.status = data;   
                    })
                    .error(function(data, status, headers, config) {
                    });
            },
            pause: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/pause?format=jsonraw&machineId=' + machine.id;
                $http.get(url)
                    .success(function(data, status, headers, config) {
                        machine.status = data;   
                    })
                    .error(function(data, status, headers, config) {
                    });
            },
            create: function (cloudspaceid, name, description, sizeId, imageId, disksize, archive, region, replication) {
                var machine = [];
                url = cloudspaceconfig.apibaseurl + '/machines/create?format=jsonraw&cloudspaceId=' + cloudspaceid + '&name=' + name + 
                    '&description=' + description + '&sizeId=' + sizeId + '&imageId=' + imageId + '&disksize=' + disksize +
                    '&archive=' + archive + '&region=' + region + '&replication=' + replication;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        machine.id = data;
                    }).error(function (data, status, headers, config) {
                    machine.error = status;
                });
                return machine;
            },
            clone: function(machine, cloneName) {
                // TODO: actual implementation
                return this.create(machine.cloudspaceId, cloneName, "Clone of " + machine.name, machine.sizeId, machine.imageId, machine.disksize);
            },
            rename: function(machine, newName) {
                machine.name = newName;
                var url = cloudspaceconfig.apibaseurl + '/machines/rename?format=jsonraw&machineId=' + machine.id + '&newName=' + newName;
                $http.get(url)
                    .success(function(data, status, headers, config) {
                    })
                    .error(function(data, status, headers, config) {
                    });
            },
            delete: function (machineid) {
                var result = []
                url = cloudspaceconfig.apibaseurl + '/machines/delete?format=jsonraw&machineId=' + machineid;
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
                url = cloudspaceconfig.apibaseurl + '/machines/list?format=jsonraw&cloudspaceId=' + cloudspaceid + '&type=';
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
                url = cloudspaceconfig.apibaseurl + '/machines/get?format=jsonraw&machineId=' + machineid;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        _.extend(machine, data);
                    }).error(
                    function (data, status, headers, config) {
                        machine.error = status;
                    });
                return machine;
            },
            listSnapshots: function (machineid) {
                var snapshotsResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/listSnapshots?format=jsonraw&machineId=' + machineid;
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
                var url = cloudspaceconfig.apibaseurl + '/machines/snapshot?format=jsonraw&machineId=' + machineId + '&snapshotName=' + snapshotName;
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
                var url = cloudspaceconfig.apibaseurl + '/machines/getConsoleUrl?format=jsonraw&machineId=' + machineId;
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
                url = cloudspaceconfig.apibaseurl + '/images/list?format=jsonraw';
                $http.get(url).success(
                    function (data, status, headers, config) {
                        _.extend(images, _.pairs(_.groupBy(data, function(img) { return img.type; })));
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
                url = cloudspaceconfig.apibaseurl + '/sizes/list?format=jsonraw';
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
