angular.module('cloudscalers.services')

    .factory('Machine', function ($http, $q) {
        $http.defaults.get = {'Content-Type': 'application/json', 'Accept': 'Content-Type: application/json'};
        var machineStates = {
            'start': 'RUNNING',
            'stop': 'HALTED',
            'pause': 'PAUSED',
            'resume': 'RUNNING'
        };
        return {
            start: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/start?machineId=' + machine.id;
                return $http.get(url).then(
                    function(result) {
                        machine.status = machineStates['start'];
                        return result.data;
                    }, 
                    function(reason){
                        return $q.reject(reason);
                    });
            },
            stop: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/stop?machineId=' + machine.id;
                return $http.get(url).then(
                    function(result) {
                        machine.status = machineStates['stop'];
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            pause: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/pause?machineId=' + machine.id;
                return $http.get(url).then(
                    function(result) {
                        machine.status = machineStates['pause'];
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            resume: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/resume?machineId=' + machine.id;
                return $http.get(url).then(
                    function(result) {
                        machine.status = machineStates['resume'];
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            create: function (cloudspaceid, name, description, sizeId, imageId, disksize, archive, region, replication) {
                var machine = [];
                url = cloudspaceconfig.apibaseurl + '/machines/create?cloudspaceId=' + cloudspaceid + '&name=' + name + 
                    '&description=' + description + '&sizeId=' + sizeId + '&imageId=' + imageId + '&disksize=' + disksize +
                    '&archive=' + archive + '&region=' + region + '&replication=' + replication;
                return $http.get(url).then(
                		function (result) {
                            return result.data;
                        },
                        function (reason){
                        	return $q.reject(reason);
                        }
                );
            },
            clone: function(machine, cloneName) {
                var url = cloudspaceconfig.apibaseurl + '/machines/clone?machineId=' + machine.id + '&name=' + cloneName;
                return $http.get(url).then(
                    function(result) {
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            delete: function (machineid) {
                url = cloudspaceconfig.apibaseurl + '/machines/delete?machineId=' + machineid;
                return $http.get(url).then(
                    function (result) {
                        return;
                    },
                    function(reason){
                    	return $q.reject(reason);
                    }
                    );
            },
            list: function (cloudspaceid) {
                url = cloudspaceconfig.apibaseurl + '/machines/list?cloudspaceId=' + cloudspaceid + '&type=';
                
                return $http.get(url).then(function(result) {
                	_.each(result.data, function (machine) {
                        if(machine.status === 'SUSPENDED'){
                            machine.status = 'PAUSED';
                        }
                    });
                    return result.data;
                    
                }, function(reason) {
                	return $q.reject(reason);
                });
            },
            get: function (machineid) {
                var machine = {
                    id: machineid
                };
                url = cloudspaceconfig.apibaseurl + '/machines/get?machineId=' + machineid;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        if(data.status === 'SUSPENDED'){
                                data.status = 'PAUSED';
                            }
                        _.extend(machine, data);
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
            createSnapshot: function (machineId, name) {
                var createSnapshotResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/snapshot?machineId=' + machineId + '&name=' + name;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        createSnapshotResult.success = true;
                    }).error(
                    function (data, status, headers, config) {
                        createSnapshotResult.error = status;
                    });
                return createSnapshotResult;
            },
            rollbackSnapshot: function (machineId, name) {
                var rollbackSnapshotResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/rollbackSnapshot?machineId=' + machineId + '&name=' + name;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        rollbackSnapshotResult.success = true;
                    }).error(
                    function (data, status, headers, config) {
                        rollbackSnapshotResult.error = status;
                    });
                return rollbackSnapshotResult;
            },
            deleteSnapshot: function (machineId, name) {
                var deleteSnapshotResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/deleteSnapshot?machineId=' + machineId + '&name=' + name;
                $http.get(url).success(
                    function (data, status, headers, config) {
                        deleteSnapshotResult.success = true;
                    }).error(
                    function (data, status, headers, config) {
                        deleteSnapshotResult.error = status;
                    });
                return deleteSnapshotResult;
            },
            getConsoleUrl: function(machineId) {
                var getConsoleUrlResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/getConsoleUrl?machineId=' + machineId;
                $http.get(url).success(function(data, status, headers, config) {
                    if (data == 'None') {
                        getConsoleUrlResult.error = status;
                    } else {
                        getConsoleUrlResult.url = JSON.parse(data);
                    }
                }).error(function (data, status, headers, config) {
                    getConsoleUrlResult.error = status;
                });
                return getConsoleUrlResult;
            },
            getHistory: function(machineId) {
                var historyResult = {};
                var url = cloudspaceconfig.apibaseurl + '/machines/getHistory?size=100&machineId=' + machineId;
                $http.get(url).success(function(data, status, headers, config) {
                    if (data == 'None') {
                        historyResult.error = status;
                    } else {
                        historyResult.history = _.sortBy(data, function(h) { return -h._source.epoch; });
                    }
                }).error(function (data, status, headers, config) {
                    historyResult.error = status;
                });
                return historyResult;
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
                        _.each(data, function(image) {
                            images.push(image);
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
