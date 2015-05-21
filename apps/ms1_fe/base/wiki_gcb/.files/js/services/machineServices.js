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
            reboot: function(machine) {
                var url = cloudspaceconfig.apibaseurl + '/machines/reboot?machineId=' + machine.id;
                return $http.get(url).then(
                    function(result) {
                        machine.status = machineStates['start'];
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
                url = cloudspaceconfig.apibaseurl + '/machines/create?cloudspaceId=' + cloudspaceid + '&name=' + encodeURIComponent(name) + 
                    '&description=' + encodeURIComponent(description) + '&sizeId=' + sizeId + '&imageId=' + imageId + '&disksize=' + disksize +
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
            updateDescription: function (id, newdescription) {
                var machine = [];
                url = cloudspaceconfig.apibaseurl + '/machines/update?machineId=' + encodeURIComponent(id) + '&description=' + 
                encodeURIComponent(newdescription);
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
                var url = cloudspaceconfig.apibaseurl + '/machines/clone?machineId=' + machine.id + '&name=' + encodeURIComponent(cloneName);
                return $http.get(url).then(
                    function(result) {
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            createTemplate: function(machine, templatename) {
                var url = cloudspaceconfig.apibaseurl + '/machines/createTemplate?machineId=' + machine.id + '&templatename=' + encodeURIComponent(templatename);
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
                return $http.get(url).then(
                    function(result) {
                        if(result.data.status === 'SUSPENDED'){
                            result.data.status = 'PAUSED';
                            _.each(result.data.acl, function (acl, i) {
                                if(acl.right.indexOf("U") > -1 && acl.right.indexOf("U") > -1){
                                    result.data.acl[i].right = "ACDRUX";
                                }
                            });
                        }
                        return _.extend(machine, result.data);
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            listSnapshots: function (machineid) {
                var url = cloudspaceconfig.apibaseurl + '/machines/listSnapshots?machineId=' + machineid;
                return $http.get(url).then(
                    function(result) {
                        return result.data;
                    },
                    function(reason) {
                        return $q.reject(reason);
                    });
            },
            createSnapshot: function (machineId, name) {
                var url = cloudspaceconfig.apibaseurl + '/machines/snapshot?machineId=' + machineId + '&name=' + encodeURIComponent(name);
                return $http.get(url).then(
                        function(result) {
                            return result.data;
                        },
                        function(reason) {
                            return $q.reject(reason);
                        });
            },
            rollbackSnapshot: function (machineId, epoch) {
                var url = cloudspaceconfig.apibaseurl + '/machines/rollbackSnapshot?machineId=' + machineId + '&epoch=' + encodeURIComponent(epoch);
                return $http.get(url).then(
                        function(result) {
                            return result.data;
                        },
                        function(reason) {
                            return $q.reject(reason);
                        });
            },
            deleteSnapshot: function (machineId, epoch) {
                var url = cloudspaceconfig.apibaseurl + '/machines/deleteSnapshot?machineId=' + machineId + '&epoch=' + encodeURIComponent(epoch);
                return $http.get(url).then(
                        function(result) {
                            return result.data;
                        },
                        function(reason) {
                            return $q.reject(reason);
                        });
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
                var url = cloudspaceconfig.apibaseurl + '/machines/getHistory?size=100&machineId=' + machineId;
                return $http.get(url);
            },
            deleteTemplate: function(templateIndex) {
                return $http.get(cloudspaceconfig.apibaseurl + '/template/delete?templateIndex=' + templateIndex)
                    .then(function(result) { 
                        return result.data; },
                          function(reason) { 
                            return $q.reject(reason); });
            },
            addUser: function(machineId, user, accessType) {
                return $http.get(cloudspaceconfig.apibaseurl + '/machines/addUser?machineId=' + machineId +
                          '&accessType=' + accessType + '&userId=' + user)
                    .then(
                            function(result){ return result.data;},
                            function(reason) { return $q.reject(reason);});
            },
            deleteUser: function(machineId, user) {
                return $http.get(cloudspaceconfig.apibaseurl + '/machines/deleteUser?machineId=' + machineId +
                                 '&userId=' + user)
                    .then(function(result) { return result.data; },
                          function(reason) { return $q.reject(reason); });
            },
            macineAccessRights: function(machineId, user) {
                var accessRights = [{
                  name: 'Read',
                  value: 'R'
                }, 
                {
                  name: 'Read/Write',
                  value: 'CRX'
                },
                {
                  name: 'Admin',
                  value: 'ACDRUX'
                }];
                return accessRights;
            },
            updateUser: function(machineId, user, accessType) {
                return $http.get(cloudspaceconfig.apibaseurl + '/machines/updateUser?machineId=' + machineId +
                                 '&userId=' + user + '&accessType=' + accessType)
                    .then(function(result) { return result.data; },
                          function(reason) { return $q.reject(reason); });
            },
        }
    })
    .factory('Image', function ($http) {
        return {
            list: function (accountid, cloudspaceid) {
                var images = [];
                url = cloudspaceconfig.apibaseurl + '/images/list?accountid=' + accountid + '&cloudspaceid=' + cloudspaceid;
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
            list: function (cloudspaceId) {
                var sizes = [];
                url = cloudspaceconfig.apibaseurl + '/sizes/list?cloudspaceId=' + cloudspaceId;
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
