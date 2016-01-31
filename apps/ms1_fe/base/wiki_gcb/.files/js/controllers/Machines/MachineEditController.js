angular.module('cloudscalers.controllers')
    .controller('MachineEditController',
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'Networks' , 'Size','confirm', '$alert', '$modal', 'LoadingDialog', '$ErrorResponseAlert',
                function($scope, $routeParams, $timeout, $location, Machine, Networks , Size, confirm, $alert, $modal, LoadingDialog, $ErrorResponseAlert) {
        $scope.tabState = "currentDisks";

        $scope.changeTabState = function(state) {
            $scope.tabState = state;
        };

        $scope.clearDisk = function(){
            $scope.disk = {name: "", size: "", description: ""};
            $scope.changeTabState('currentDisks');
        }
        $scope.clearDisk();

        $scope.getMachine = function(){
            return Machine
                .get($routeParams.machineId)
                .then(function(data) {
                    $scope.machine = data;
                    $timeout(function () {
                        LoadingDialog.hide();
                    }, 1500);
                },function(reason) {
                    LoadingDialog.hide();
                    $ErrorResponseAlert(reason);
                });
        }
        $scope.getMachine();

        $scope.createDisk = function() {
            LoadingDialog.show('Creating disk');
            Machine.addDisk($routeParams.machineId, $scope.disk.name, $scope.disk.description, $scope.disk.size, "D").then(function(result){
                $scope.getMachine();
                $scope.clearDisk();
            },function(reason){
                LoadingDialog.hide();
                $ErrorResponseAlert(reason);
            });
        };

        $scope.removeDisk = function(disk) {
            var modalInstance = $modal.open({
                templateUrl: 'removeDiskDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.disk = disk;
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                LoadingDialog.show('Removing disk');
                Machine.removeDisk(disk.id, true).then(function(result){
                    $scope.machine.disks.splice( $scope.machine.disks.indexOf(disk), 1);
                    LoadingDialog.hide();
                },function(reason){
                    $ErrorResponseAlert(reason);
                    LoadingDialog.hide();
                });
            });

        };

        $scope.moveDisk = function(disk, currentSpace) {
            if($scope.machine.status != "HALTED"){
                $alert("Machine must be stopped to move disk.");
                return;
            }
            var modalInstance = $modal.open({
                templateUrl: 'moveDiskDialog.html',
                controller: function($scope, $modalInstance){
                    var currentMachine = _.find(currentSpace.machines , function(machine) { return machine.id == $routeParams.machineId; });
                    if(currentMachine){
                        currentSpace.machines.splice( currentSpace.machines.indexOf(currentMachine), 1);
                    }
                    $scope.currentSpace = currentSpace;
                    $scope.disk = disk;
                    $scope.diskDestination = currentSpace.machines[0];
                    $scope.ok = function (diskDestination) {
                        LoadingDialog.show('Moving disk');
                        Machine.moveDisk(diskDestination.id, disk.id).then(function(result){
                            LoadingDialog.hide();
                            $modalInstance.close('ok');
                        },function(reason){
                            $ErrorResponseAlert(reason);
                            LoadingDialog.hide();
                        });
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                $scope.machine.disks.splice( $scope.machine.disks.indexOf(disk), 1);
            });

        };

        $scope.isDataDisk = function(disk){
           return disk.type != 'B';
        }

        $scope.isValidCreateDisk = function(){
            return $scope.disk.name != '' && $scope.disk.size != '' && $scope.disk.size >= 1 && $scope.disk.size <= 2000;
        }

        $scope.$watch('machine.acl', function (acl) {
            if(acl === undefined ) {
                return;
            }
            if($scope.currentUser.username && $scope.machine.acl && !$scope.currentUserAccess){
                var currentUserAccessright =  _.find($scope.machine.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; }).right.toUpperCase();
                if(currentUserAccessright == "R"){
                    $scope.currentUserAccess = 'Read';
                }else if( currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') == -1 && currentUserAccessright.indexOf('U') == -1){
                    $scope.currentUserAccess = "ReadWrite";
                }else if(currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') != -1 && currentUserAccessright.indexOf('U') != -1){
                    $scope.currentUserAccess = "Admin";
                }
            }
        }, true);

        $scope.tabactive = {actions: true, console: false, snapshots: false, changelog: false};

        var changeSelectedTab = function(tab){
            if (tab){
                $scope.tabactive.actions = (tab=='actions');
                $scope.tabactive.console = (tab == 'console');
                $scope.tabactive.snapshots = (tab=='snapshots');
                $scope.tabactive.changelog = (tab=='changelog');
                $scope.tabactive.portForwards = (tab=='portForwards');
                $scope.tabactive.sharing = (tab=='sharing');
            }
        }

        changeSelectedTab($routeParams.activeTab);

        var retrieveMachineHistory = function() {
            $scope.machineHistory = {};
            Machine.getHistory($routeParams.machineId)
                .then(function(data) {
                    $scope.refreshSpinner = false;
                    $scope.machineHistory = data;
                },
                function(reason) {
                    $scope.refreshSpinner = false;
                    $ErrorResponseAlert(reason);
                });
        };

        $scope.$watch('tabactive.changelog', function() {
            if (!$scope.tabactive.changelog)
                return;
            retrieveMachineHistory();
        }, true);

        $scope.oldMachine = {};
        $scope.imagesList = [];
        $scope.machineinfo = {};

        var updateMachineSize = function(){
            $scope.$watch('machine', function() {
                if($scope.machine){
                    $scope.machineinfo = {};
                    size = _.findWhere($scope.sizes, { id: $scope.machine.sizeid });
                    $scope.machineinfo['size'] = size;
                    image = _.findWhere($scope.images, { id: $scope.machine.imageid });
                    $scope.machineinfo['image'] = image;
                    $scope.machineinfo['storage'] = $scope.machine.storage;
                    }
            }, true);
        };

        $scope.$watch('images', function() {
            $scope.imagesList = _.flatten(_.values(_.object($scope.images)));
        });

        $scope.$watch('machine', function() {
            angular.copy($scope.machine, $scope.oldMachine);
        }, true);

        $scope.$watch('machine', updateMachineSize, true);
        $scope.$watch('sizes', updateMachineSize, true);
        $scope.$watch('images', updateMachineSize, true);

        $scope.resize = function(currentSpace) {
            var sizes = $scope.sizes,
                initialSizeId = $scope.machine.sizeid;

            var modalInstance = $modal.open({
                templateUrl: 'resizeMachineDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.sizes = sizes;
                    $scope.sizepredicate = 'memory'
                    $scope.numeral = numeral;
                    $scope.initialSizeId = initialSizeId;

                    $scope.selectedPackage = _.find($scope.sizes, function(size) {
                        return size.id === $scope.initialSizeId;
                    });


                    $scope.setPackage = function(package) {
                        $scope.selectedPackage = package;
                    };

                    $scope.ok = function() {
                        $modalInstance.close($scope.selectedPackage);
                    };
                    
                    $scope.cancel = function() {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (size) {
                LoadingDialog.show('Resizing compute capacity..');
                
                Machine
                    .resize($scope.machine.id, size.id)
                    .then(function() {
                        return $scope
                            .getMachine();
                    })
                    .then(null, function() {
                        $ErrorResponseAlert(error);
                    })
                    ['finally'](function() {
                        LoadingDialog.hide();
                    })
            });
        };

        $scope.destroy = function() {
            var modalInstance = $modal.open({
                templateUrl: 'destroyMachineDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                LoadingDialog.show('Deleting machine');
                Machine.delete($scope.machine.id).then(function(){
                    var machine = _.find($scope.machines, function(machine){ return machine.id == $scope.machine.id;});
                    if (machine){
                        machine.status = 'DESTROYED';
                    }
                    $scope.machines.splice($scope.machines.indexOf(machine) , 1);
                    $location.path("/list");
                    LoadingDialog.hide();
                }, function(reason) {
                    LoadingDialog.hide();
                    $ErrorResponseAlert(reason);
                });

            });
        };

        var updatesnapshots = function(){
            $scope.snapshots = {};
            $scope.snapshotsLoader = true;
            Machine.listSnapshots($routeParams.machineId).then(function(data) {
                $scope.snapshots = data;
                $scope.snapshotsLoader = false;
                $timeout(function () {
                  LoadingDialog.hide();
                }, 1500);
                $scope.refreshSpinner = false;
            }, function(reason) {
                $scope.refreshSpinner = false;
                $ErrorResponseAlert(reason);
            });
        }
        updatesnapshots();

        var CreateSnapshotController = function ($scope, $modalInstance) {

            $scope.snapshotname= '';

            $scope.submit = function (result) {
                $modalInstance.close(result.newSnapshotName);
            };

            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        };

        $scope.$watch('tabactive.snapshots', function() {
            if (!$scope.tabactive.snapshots)
                return;
            updatesnapshots();
        }, true);

        $scope.createSnapshot = function() {
            var modalInstance = $modal.open({
                templateUrl: 'createSnapshotDialog.html',
                controller: CreateSnapshotController,
                resolve: {
                }
            });

            modalInstance.result.then(function (snapshotname) {
                LoadingDialog.show('Creating snapshot');
                Machine.createSnapshot($scope.machine.id, snapshotname).then(
                    function(result){
                        updatesnapshots();
                    },
                    function(reason){
                        $timeout(function () {
                          LoadingDialog.hide();
                        }, 1500);
                        $ErrorResponseAlert(reason);
                    }
                );
            });
        };

        $scope.rollbackSnapshot = function(snapshot) {

            if ($scope.machine.status != "HALTED"){
                $alert("A snapshot can only be rolled back to a stopped machine.");
                return;
            }

            var modalInstance = $modal.open({
                templateUrl: 'rollbackSnapshotDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                LoadingDialog.show('Rolling back snapshot');
                Machine.rollbackSnapshot($scope.machine.id, snapshot.epoch).then(
                        function(result){
                            LoadingDialog.hide();
                            var removedSnapshot = _.where($scope.snapshots, {epoch: snapshot.epoch})[0];
                            $scope.snapshots.splice( $scope.snapshots.indexOf(removedSnapshot) , 1);
                        }, function(reason){
                            LoadingDialog.hide();
                            $alert(reason.data);
                        }
                    ) ;
            });
        };

        $scope.deleteSnapshot = function(snapshot) {
            var modalInstance = $modal.open({
                templateUrl: 'deleteSnapshotDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDestroy = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                LoadingDialog.show('Deleting snapshot');
                Machine.deleteSnapshot($scope.machine.id, snapshot.epoch).then(
                    function(result){
                        LoadingDialog.hide();
                        var removedSnapshot = _.where($scope.snapshots, {epoch: snapshot.epoch})[0];
                        $scope.snapshots.splice( $scope.snapshots.indexOf(removedSnapshot) , 1);
                    }, function(reason){
                        LoadingDialog.hide();
                        $alert(reason.data);
                    }
                );
            });

        };


        var CloneMachineController= function ($scope, $modalInstance) {

            $scope.clone ={name: ''};

            $scope.ok = function () {
                    $modalInstance.close($scope.clone.name);
            };

            $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
            };
        };

        var CreateTemplateController= function ($scope, $modalInstance) {

            $scope.createtemplate ={name: ''};

            $scope.ok = function () {
                    $modalInstance.close($scope.createtemplate.name);
            };

            $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
            };
        };

        $scope.cloneMachine = function() {

            if ($scope.machine.status != "HALTED"){
                $alert("A clone can only be taken from a stopped machine.");
                return;
            }
            var modalInstance = $modal.open({
                    templateUrl: 'cloneMachineDialog.html',
                    controller: CloneMachineController,
                    resolve: {
                    }
                });

                modalInstance.result.then(function (cloneName) {
                    LoadingDialog.show('Creating clone');
                    Machine.clone($scope.machine, cloneName).then(
                        function(result){
                            LoadingDialog.hide();
                            $location.path("/edit/" + result);
                        },
                        function(reason){
                            LoadingDialog.hide();
                            $alert(reason.data);
                        }
                    );
                });
        };


        $scope.createTemplate = function() {


            var modalInstance = $modal.open({
                    templateUrl: 'createTemplateDialog.html',
                    controller: CreateTemplateController,
                    resolve: {
                    }
                });

                modalInstance.result.then(function (templatename) {
                    LoadingDialog.show('Creating Template');
                    Machine.createTemplate($scope.machine, templatename).then(
                        function(result){
                            LoadingDialog.hide();
                            $scope.machine.locked = true;
                        },
                        function(reason){
                            LoadingDialog.hide();
                            $alert(reason.data);
                        }
                    );
                });
        };
        $scope.refreshSpinner = false;
        $scope.refreshData = function() {
            if($scope.tabactive.actions || $scope.tabactive.sharing || $scope.tabactive.console){
                $scope.refreshSpinner = true;
                Machine.get($routeParams.machineId).then(function(data) {
                    $scope.machine = data;
                    $scope.refreshSpinner = false;
                },
                function(reason) {
                    $scope.refreshSpinner = false;
                    $ErrorResponseAlert(reason);
                });
            }else if($scope.tabactive.changelog){
                $scope.refreshSpinner = true;
                retrieveMachineHistory();
            }
            else if($scope.tabactive.portForwards){
                $scope.refreshSpinner = true;
                Networks.listPortforwarding($scope.currentSpace.id, $routeParams.machineId).then(
                    function(data) {
                      $scope.portforwarding = data;
                      $scope.refreshSpinner = false;
                    },
                    function(reason) {
                      $ErrorResponseAlert(reason);
                      $scope.refreshSpinner = false;
                    }
                );
            }else if($scope.tabactive.snapshots){
                $scope.refreshSpinner = true;
                updatesnapshots();
            }
        };

        $scope.start = function() {
            LoadingDialog.show('Starting');
            Machine.start($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    changeSelectedTab('console');
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data.backtrace);
                }
            );

        };

        $scope.reboot = function() {
            LoadingDialog.show('Rebooting');
            Machine.reboot($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    changeSelectedTab('console');
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data.backtrace);
                }
            );

        };

        $scope.reset = function() {
            LoadingDialog.show('Reseting');
            Machine.reset($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    changeSelectedTab('console');
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data.backtrace);
                }
            );

        };

         $scope.stop = function() {
            LoadingDialog.show('Stopping');
             Machine.stop($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $alert(reason.data);
                }
            );
        };

        $scope.pause = function() {
            LoadingDialog.show('Pausing');
            Machine.pause($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $ErrorResponseAlert(reason);
                }
            );
        };

        $scope.resume = function() {
            LoadingDialog.show('Resuming');
            Machine.resume($scope.machine).then(
                function(result){
                    LoadingDialog.hide();
                    $scope.updateMachineList();
                },
                function(reason){
                    LoadingDialog.hide();
                    $ErrorResponseAlert(reason);
                }
            );
        };
        $scope.updateDescriptionPopup = function () {
            $scope.modalInstance = $modal.open({
                templateUrl: 'updateDescription.html',
                controller: updateDescriptionController,
                resolve: {},
                scope: $scope
            });
        };
        var updateDescriptionController = function($modalInstance) {
            $scope.machine.newdescription = $scope.machine.description;
            $scope.submit = function () {
                Machine.updateDescription($scope.machine.id, $scope.machine.newdescription).then(
                    function(machineId){
                        $scope.machine.description = $scope.machine.newdescription;
                        $modalInstance.close({});
                    },
                    function(reason){
                        $modalInstance.close({});
                        $ErrorResponseAlert(reason);
                    }
                );
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        };
    }]);
