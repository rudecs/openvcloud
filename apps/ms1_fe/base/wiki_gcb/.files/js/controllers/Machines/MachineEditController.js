(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('MachineEditController', MachineEditController);

  function MachineEditController($scope, $routeParams, $timeout, $location, Machine,
    Networks, Size, confirm, $alert, $modal, LoadingDialog, $ErrorResponseAlert) {
    $scope.tabState = 'currentDisks';
    $scope.oldMachine = {};
    $scope.imagesList = [];
    $scope.machineinfo = {};
    $scope.changeTabState = changeTabState;
    $scope.clearDisk = clearDisk;
    $scope.getMachine = getMachine;
    $scope.createDisk = createDisk;
    $scope.removeDisk = removeDisk;
    $scope.moveDisk = moveDisk;
    $scope.isValidCreateDisk = isValidCreateDisk;
    $scope.resize = resize;
    $scope.destroy = destroy;
    $scope.createSnapshot = createSnapshot;
    $scope.rollbackSnapshot = rollbackSnapshot;
    $scope.deleteSnapshot = deleteSnapshot;
    $scope.cloneMachine = cloneMachine;
    $scope.createTemplate = createTemplate;
    $scope.refreshSpinner = false;
    $scope.refreshData = refreshData;
    $scope.start = start;
    $scope.reboot = reboot;
    $scope.reset = reset;
    $scope.stop = stop;
    $scope.pause = pause;
    $scope.resume = resume;
    $scope.updateDescriptionPopup = updateDescriptionPopup;
    $scope.tabactive = {
        actions: true,
        console: false,
        snapshots: false,
        changelog: false
      };

    //Binding and Watch
    $scope.$watch('machine.acl', machineACL, true);
    $scope.$watch('tabactive.changelog', tabActiveChangeLog, true);
    $scope.$watch('images', images);
    $scope.$watch('machine', machine, true);
    $scope.$watch('machine', updateMachineSize, true);
    $scope.$watch('sizes', updateMachineSize, true);
    $scope.$watch('images', updateMachineSize, true);
    $scope.$watch('tabactive.snapshots', tabActiveSpanShots, true);

    // Initialization: Functions invokation logic
    $scope.clearDisk();
    $scope.getMachine();
    changeSelectedTab($routeParams.activeTab);
    updatesnapshots();

    // Functions
    function changeTabState(state) {
      $scope.tabState = state;
    }

    function clearDisk() {
      $scope.disk = {name: '', size: '', description: ''};
      $scope.changeTabState('currentDisks');
    }

    function getMachine() {
      return Machine
        .get($routeParams.machineId)
        .then(function(data) {
          $scope.machine = data;
          $timeout(function() {
            LoadingDialog.hide();
          }, 1500);
        },function(reason) {
          LoadingDialog.hide();
          $ErrorResponseAlert(reason);
        }
      );
    }

    function createDisk() {
      LoadingDialog.show('Creating disk');
      Machine.addDisk($routeParams.machineId, $scope.disk.name,
        $scope.disk.description, $scope.disk.size, 'D').then(function() {
          $scope.getMachine();
          $scope.clearDisk();
        },function(reason) {
          LoadingDialog.hide();
          $ErrorResponseAlert(reason);
        }
      );
    }

    function removeDisk(disk) {
      var modalInstance = $modal.open({
        templateUrl: 'removeDiskDialog.html',
        controller: function($scope, $modalInstance) {
          $scope.disk = disk;
          $scope.ok = function() {
            $modalInstance.close('ok');
          };
          $scope.cancelDestroy = function() {
            $modalInstance.dismiss('cancel');
          };
        },
        resolve: {}
      });

      modalInstance.result.then(function() {
        LoadingDialog.show('Removing disk');
        Machine.removeDisk(disk.id, true).then(function() {
          $scope.machine.disks.splice($scope.machine.disks.indexOf(disk), 1);
          LoadingDialog.hide();
        },function(reason) {
          $ErrorResponseAlert(reason);
          LoadingDialog.hide();
        });
      });
    }

    function moveDisk(disk, currentSpace, machines) {
      if ($scope.machine.status !== 'HALTED') {
        $alert('Machine must be stopped to move disk.');
        return;
      }
      var modalInstance = $modal.open({
        templateUrl: 'moveDiskDialog.html',
        controller: function($scope, $modalInstance) {
          $scope.machines = machines;
          var currentMachine = _.find($scope.machines , function(machine) {
            return machine.id === $routeParams.machineId;
          });
          if (currentMachine) {
            $scope.machines.splice($scope.machines.indexOf(currentMachine), 1);
          }
          $scope.currentSpace = currentSpace;
          $scope.disk = disk;
          $scope.diskDestination = $scope.machines[0];
          $scope.ok = function(diskDestination) {
            LoadingDialog.show('Moving disk');
            Machine.moveDisk(diskDestination.id, disk.id)
            .then(
              function() {
                LoadingDialog.hide();
                $modalInstance.close('ok');
              },function(reason) {
                $ErrorResponseAlert(reason);
                LoadingDialog.hide();
              }
            );
          };
          $scope.cancelDestroy = function() {
            $modalInstance.dismiss('cancel');
          };
        },
        resolve: {}
      });

      modalInstance.result.then(function() {
        $scope.machine.disks.splice($scope.machine.disks.indexOf(disk), 1);
      });
    }

    function isValidCreateDisk() {
      return $scope.disk.name !== '' &&
        $scope.disk.size !== '' &&
        $scope.disk.size >= 1 &&
        $scope.disk.size <= 2000;
    }

    function machineACL(acl) {
      if ($scope.currentUser.username && acl && $scope.currentAccount.status !== 'DISABLED') {
        $scope.currentUser.acl.machine = 0;
        var currentUserAccessright = _.find($scope.machine.acl ,function(acl) {
              return acl.userGroupId === $scope.currentUser.username;
            }).right.toUpperCase();
        if (currentUserAccessright === 'R') {
          $scope.currentUser.acl.machine = 1;
        }else if (currentUserAccessright.search(/R|C|X/) !== -1 && currentUserAccessright.search(/D|U/) === -1) {
          $scope.currentUser.acl.machine = 2;
        }else if (currentUserAccessright.search(/R|C|X|D|U/) !== -1) {
          $scope.currentUser.acl.machine = 3;
        }
      }
    }

    function changeSelectedTab(tab) {
      if (tab) {
        $scope.tabactive.actions = (tab === 'actions');
        $scope.tabactive.console = (tab === 'console');
        $scope.tabactive.snapshots = (tab === 'snapshots');
        $scope.tabactive.changelog = (tab === 'changelog');
        $scope.tabactive.portForwards = (tab === 'portForwards');
        $scope.tabactive.sharing = (tab === 'sharing');
      }
    }

    function retrieveMachineHistory() {
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
    }

    function tabActiveChangeLog() {
      if (!$scope.tabactive.changelog) {
        return;
      }
      retrieveMachineHistory();
    }

    function updateMachineSize() {
      $scope.$watch('machine', function() {
          if ($scope.machine) {
            $scope.machineinfo = {};
            var size = _.findWhere($scope.sizes, {id: $scope.machine.sizeid});
            $scope.machineinfo['size'] = size;
            var image = _.findWhere($scope.images, {id: $scope.machine.imageid});
            $scope.machineinfo['image'] = image;
            $scope.machineinfo['storage'] = $scope.machine.storage;
          }
        }, true);
    }

    function images() {
      $scope.imagesList = _.flatten(_.values(_.object($scope.images)));
    }

    function machine() {
      angular.copy($scope.machine, $scope.oldMachine);
    }

    function resize(currentSpace, status) {
      if (status !== 'HALTED') {
        return;
      }

      var sizes = $scope.sizes;
      var initialSizeId = $scope.machine.sizeid;

      var modalInstance = $modal.open({
        templateUrl: 'resizeMachineDialog.html',
        controller: function($scope, $modalInstance) {
          $scope.sizes = sizes;
          $scope.sizepredicate = 'memory';
          $scope.numeral = numeral;
          $scope.initialSizeId = initialSizeId;

          $scope.selectedPackage = _.find($scope.sizes, function(size) {
            return size.id === $scope.initialSizeId;
          });

          $scope.setPackage = function(bundle) {
            $scope.selectedPackage = bundle;
          };
          $scope.ok = function() {
            $modalInstance.close($scope.selectedPackage);
          };

          $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
          };
        },
        resolve: {}
      });

      modalInstance.result.then(function(size) {
        LoadingDialog.show('Resizing compute capacity..');

        Machine.resize($scope.machine.id, size.id)
        .then(
          function() {
            return $scope.getMachine();
          }, function(error) {
            $ErrorResponseAlert(error);
          })['finally'](function() {
            LoadingDialog.hide();
          });
      });
    }

    function destroy() {
      var modalInstance = $modal.open({
        templateUrl: 'destroyMachineDialog.html',
        controller: function($scope, $modalInstance) {
          $scope.ok = function() {
            $modalInstance.close('ok');
          };
          $scope.cancelDestroy = function() {
            $modalInstance.dismiss('cancel');
          };
        },
        resolve: {}
      });

      modalInstance.result.then(function() {
        LoadingDialog.show('Deleting machine');
        Machine.delete($scope.machine.id).then(function() {
          var machine = _.find($scope.machines, function(machine) {
            return machine.id === $scope.machine.id;
          });
          if (machine) {
            machine.status = 'DESTROYED';
          }
          $scope.machines.splice($scope.machines.indexOf(machine) , 1);
          $location.path('/list');
          LoadingDialog.hide();
        }, function(reason) {
          LoadingDialog.hide();
          $ErrorResponseAlert(reason);
        });
      });
    }

    function updatesnapshots() {
      $scope.snapshots = [];
      $scope.snapshotsLoader = true;
      Machine.listSnapshots($routeParams.machineId).then(function(data) {
          $scope.snapshots = data;
          $scope.snapshotsLoader = false;
          $timeout(function() {
            LoadingDialog.hide();
          }, 1500);
          $scope.refreshSpinner = false;
        }, function(reason) {
          $scope.refreshSpinner = false;
          $ErrorResponseAlert(reason);
        });
    }

    function CreateSnapshotController($scope, $modalInstance) {
      $scope.snapshotname = '';
      $scope.submit = function(result) {
        $modalInstance.close(result.newSnapshotName);
      };

      $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
      };
    }

    function tabActiveSpanShots() {
      if (!$scope.tabactive.snapshots) { return; }
      updatesnapshots();
    }

    function createSnapshot() {
      var modalInstance = $modal.open({
        templateUrl: 'createSnapshotDialog.html',
        controller: CreateSnapshotController,
        resolve: {}
      });

      modalInstance.result.then(function(snapshotname) {
        LoadingDialog.show('Creating snapshot');
        Machine.createSnapshot($scope.machine.id, snapshotname).then(
            function() {
              updatesnapshots();
            },
            function(reason) {
              $timeout(function() {
                  LoadingDialog.hide();
                }, 1500);
              $ErrorResponseAlert(reason);
            }
        );
      });
    }

    function rollbackSnapshot(snapshot) {
      if ($scope.machine.status !== 'HALTED') {
        $alert('A snapshot can only be rolled back to a stopped machine.');
        return;
      }

      var modalInstance = $modal.open({
          templateUrl: 'rollbackSnapshotDialog.html',
          controller: function($scope, $modalInstance) {
            $scope.ok = function() {
              $modalInstance.close('ok');
            };
            $scope.cancelDestroy = function() {
              $modalInstance.dismiss('cancel');
            };
          },
          resolve: {}
        });

      modalInstance.result.then(function() {
          LoadingDialog.show('Rolling back snapshot');
          Machine.rollbackSnapshot($scope.machine.id, snapshot.epoch).then(
            function() {
              LoadingDialog.hide();
              for (var i = $scope.snapshots.length - 1; i > 0; i--) {
                if ($scope.snapshots[i].epoch > snapshot.epoch) {
                  $scope.snapshots.splice(i, 1);
                }
              }
            }, function(reason) {
              LoadingDialog.hide();
              $alert(reason.data);
            }
          );
        });
    }

    function deleteSnapshot(snapshot) {
      var modalInstance = $modal.open({
          templateUrl: 'deleteSnapshotDialog.html',
          controller: function($scope, $modalInstance) {
            $scope.ok = function() {
              $modalInstance.close('ok');
            };
            $scope.cancelDestroy = function() {
              $modalInstance.dismiss('cancel');
            };
          },
          resolve: {}
        });

      modalInstance.result.then(function() {
          LoadingDialog.show('Deleting snapshot');
          Machine.deleteSnapshot($scope.machine.id, snapshot.epoch).then(
            function() {
              LoadingDialog.hide();
              var removedSnapshot = _.where($scope.snapshots, {epoch: snapshot.epoch})[0];
              $scope.snapshots.splice($scope.snapshots.indexOf(removedSnapshot) , 1);
            }, function(reason) {
              LoadingDialog.hide();
              $alert(reason.data);
            });
        });
    }

    function CloneMachineController($scope, $modalInstance) {
        $scope.clone = {name: ''};
        $scope.ok = function() {
            $modalInstance.close($scope.clone.name);
          };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
          };
      }

    function CreateTemplateController($scope, $modalInstance) {
        $scope.createtemplate = {name: ''};
        $scope.ok = function() {
            $modalInstance.close($scope.createtemplate.name);
          };
        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
          };
      }

    function cloneMachine() {
        if ($scope.machine.status !== 'HALTED') {
          $alert('A clone can only be taken from a stopped machine.');
          return;
        }
        var modalInstance = $modal.open({
          templateUrl: 'cloneMachineDialog.html',
          controller: CloneMachineController,
          resolve: {
          }
        });

        modalInstance.result.then(function(cloneName) {
          LoadingDialog.show('Creating clone');
          Machine.clone($scope.machine, cloneName).then(
            function(result) {
              LoadingDialog.hide();
              $location.path('/edit/' + result);
            },
            function(reason) {
              LoadingDialog.hide();
              $alert(reason.data);
            }
          );
        });
      }

    function createTemplate() {
        var modalInstance = $modal.open({
          templateUrl: 'createTemplateDialog.html',
          controller: CreateTemplateController,
          resolve: {}
        });

        modalInstance.result.then(function(templatename) {
          LoadingDialog.show('Creating Template');
          Machine.createTemplate($scope.machine, templatename).then(
            function() {
              LoadingDialog.hide();
              $scope.machine.locked = true;
            },
            function(reason) {
              LoadingDialog.hide();
              $alert(reason.data);
            }
          );
        });
      }

    function refreshData() {
        if ($scope.tabactive.actions || $scope.tabactive.sharing || $scope.tabactive.console) {
          $scope.refreshSpinner = true;
          Machine.get($routeParams.machineId)
          .then(
            function(data) {
              $scope.machine = data;
              $scope.refreshSpinner = false;
            },
            function(reason) {
              $scope.refreshSpinner = false;
              $ErrorResponseAlert(reason);
            });
        }else if ($scope.tabactive.changelog) {
          $scope.refreshSpinner = true;
          retrieveMachineHistory();
        } else if ($scope.tabactive.portForwards) {
          $scope.refreshSpinner = true;
          Networks.listPortforwarding($scope.currentSpace.id, $routeParams.machineId)
          .then(
            function(data) {
              $scope.portforwarding = data;
              $scope.refreshSpinner = false;
            },
            function(reason) {
              $ErrorResponseAlert(reason);
              $scope.refreshSpinner = false;
            }
          );
        }else if ($scope.tabactive.snapshots) {
          $scope.refreshSpinner = true;
          updatesnapshots();
        }
      }

    function start() {
        LoadingDialog.show('Starting');
        Machine.start($scope.machine).then(
          function() {
            LoadingDialog.hide();
            changeSelectedTab('console');
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $alert(reason.data.backtrace);
          }
        );
      }

    function reboot() {
        LoadingDialog.show('Rebooting');
        Machine.reboot($scope.machine).then(
          function() {
            LoadingDialog.hide();
            changeSelectedTab('console');
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $alert(reason.data.backtrace);
          }
        );
      }

    function reset() {
        LoadingDialog.show('Reseting');
        Machine.reset($scope.machine).then(
          function() {
            LoadingDialog.hide();
            changeSelectedTab('console');
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $alert(reason.data.backtrace);
          }
        );
      }

    function stop() {
      LoadingDialog.show('Stopping');
      Machine.stop($scope.machine).then(
          function() {
            LoadingDialog.hide();
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $alert(reason.data);
          }
        );
    }

    function pause() {
      LoadingDialog.show('Pausing');
      Machine.pause($scope.machine).then(
          function() {
            LoadingDialog.hide();
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $ErrorResponseAlert(reason);
          }
        );
    }

    function resume() {
      LoadingDialog.show('Resuming');
      Machine.resume($scope.machine).then(
          function() {
            LoadingDialog.hide();
            $scope.updateMachineList();
          },
          function(reason) {
            LoadingDialog.hide();
            $ErrorResponseAlert(reason);
          }
        );
    }

    function updateDescriptionController($modalInstance) {
      $scope.machine.newdescription = $scope.machine.description;
      $scope.submit = function() {
          Machine.updateDescription($scope.machine.id, $scope.machine.newdescription)
          .then(
            function() {
              $scope.machine.description = $scope.machine.newdescription;
              $modalInstance.close({});
            },function(reason) {
              $modalInstance.close({});
              $ErrorResponseAlert(reason);
            }
          );
        };
      $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
        };
    }

    function updateDescriptionPopup() {
      $scope.modalInstance = $modal.open({
          templateUrl: 'updateDescription.html',
          controller: updateDescriptionController,
          resolve: {},
          scope: $scope
        });
    }
  }

})();
