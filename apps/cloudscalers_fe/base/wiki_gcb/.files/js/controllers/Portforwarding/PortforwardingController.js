angular.module('cloudscalers.controllers')
    .controller('PortforwardingController', ['$scope', 'Networks', 'Machine', '$modal', '$timeout','$ErrorResponseAlert',
        function ($scope, Networks, Machine, $modal, $timeout,$ErrorResponseAlert) {
            $scope.search = "";
            $scope.portforwardbyID = "";
            $scope.portforwarding = [];
            $scope.commonPortVar = "";
            $scope.$watch('currentSpace.id',function(){
                if ($scope.currentSpace){
                    $scope.managementui = "http://" + $scope.currentSpace.publicipaddress + "/webfig/";
                    Machine.list($scope.currentSpace.id).then(function(data) {
                      $scope.currentSpace.machines = data;
                    });
                }
            });
            Networks.listPortforwarding($scope.currentSpace.id).then(function(data) {
                $scope.portforwarding = data;
            });

            Networks.commonports().then(function(data) {
                $scope.commonports = data;
            });

            // commonports auto suggest
            Networks.commonports("...").then(function(data) {
              $scope.commonPorts = data;
            });

            $scope.suggestCommonPorts = function(typedport){
              Networks.commonports(typedport).then(function(data) {
                $scope.commonPorts = data;
              });
            };

            var addRuleController = function ($scope, $modalInstance) {
                $scope.newRule = {
                    ip: $scope.currentSpace.publicipaddress,
                    publicPort: '',
                    VM: $scope.currentSpace.machines[0],
                    localPort: '',
                    commonPort: '',
                    // message: false,
                    statusMessage: ''
                };

                $scope.updateCommonPorts = function () {
                    $scope.newRule.publicPort  = $scope.newRule.commonPort.port;
                    $scope.newRule.localPort = $scope.newRule.commonPort.port;
                };

                $scope.submit = function () {
                    
                    $modalInstance.close({
                    	cloudspaceId: $scope.currentSpace.id,
                    	publicipaddress: $scope.currentSpace.publicipaddress,
                    	publicport: $scope.newRule.publicPort,
                    	vmid: $scope.newRule.VM.id,
                    	localport: $scope.newRule.localPort,
                    	vmname: $scope.newRule.VM.name
                    });
                };
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
            };
            $scope.portForwardPopup = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'portForwardDialog.html',
                    controller: addRuleController,
                    resolve: {},
                    scope: $scope
                });
                modalInstance.result.then(function(data){
                	Networks.createPortforward(data.cloudspaceId, data.publicipaddress, data.publicport, data.vmid, data.localport).then(
                            function (result) {
                                $scope.portforwarding.push({publicIp: data.publicipaddress, publicPort: data.publicport,
                                vmName: data.vmname, vmid: data.vmid, localPort: data.localport});
                            },
                            function(reason){
                            	$ErrorResponseAlert(reason);
                            }
                        );
                });
            };
            $scope.tableRowClicked = function (index) {
              var modalInstance = $modal.open({templateUrl: 'editPortForwardDialog.html', scope: $scope , resolve: {}});
              $scope.editRule = [];
              $scope.editRule.commonPort = "";
              Networks.listPortforwarding($scope.currentSpace.id).then(function(data) {
                $scope.portforwardbyID = data;
                $scope.editRule = {
                    id: index.id,
                    ip: $scope.portforwardbyID[index.id].publicIp,
                    publicPort: $scope.portforwardbyID[index.id].publicPort,
                    VM: {'name': $scope.portforwardbyID[index.id].vmName , 'id': $scope.portforwardbyID[index.id].vmid},
                    localPort: $scope.portforwardbyID[index.id].localPort
                };
              });
              
              $scope.update = function () {
                  Networks.updatePortforward($scope.currentSpace.id, $scope.editRule.id, $scope.editRule.ip, $scope.editRule.publicPort, $scope.editRule.VM.id, $scope.editRule.localPort).then(
                      function (result) {
                          $scope.portforwarding = result.data;
                          $scope.search = $scope.portforwarding[0];
                          modalInstance.close({});
                          $scope.message = true;
                          $scope.statusMessage = "Saved!";
                          $timeout(function() {
                              $scope.message = false;
                          }, 3000);
                      }
                  );
              };
              $scope.delete = function () {
                  Networks.deletePortforward($scope.currentSpace.id, $scope.editRule.id).then(
                      function (result) {
                          $scope.portforwarding = result.data;
                          $scope.search = $scope.portforwarding[0];
                          modalInstance.close({});
                          $scope.message = true;
                          $scope.statusMessage = "Removed!";
                          $timeout(function() {
                              $scope.message = false;
                          }, 3000);
                      }
                  );
              };
              $scope.cancel = function () {
                    modalInstance.dismiss('cancel');
              };

              // $scope.$watch('editRule.publicPort',function(){
              //   if ($scope.editRule.publicPort){
              //     // console.log($scope.editRule.publicPort);
              //   }
              // });
              $scope.updateCommonPorts = function () {
                //////////////////
                    alert("sss");
                    $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
                    $scope.editRule.localPort = $scope.editRule.commonPort.port;
                };
            }
        }
    ]).filter('groupBy', function(){
        return function(list, group_by) {
        var filtered = [];
        var prev_item = null;
        var group_changed = false;
        var new_field = group_by + '_CHANGED';
        angular.forEach(list, function(item) {
            group_changed = false;
            if (prev_item !== null) {
                if (prev_item[group_by] !== item[group_by]) {
                    group_changed = true;
                }
            } else {
                group_changed = true;
            }
            if (group_changed) {
                item[new_field] = true;
            } else {
                item[new_field] = false;
            }
            filtered.push(item);
            prev_item = item;
        });
        return filtered;
        };
    }).filter('unique', function() {
       return function(collection, keyname) {
          var output = [],
              keys = [];

          angular.forEach(collection, function(item) {
              var key = item[keyname];
              if(keys.indexOf(key) === -1) {
                  keys.push(key);
                  output.push(item);
              }
          });

          return output;
       };
    }).directive('numbersOnly', function(){
   return {
     require: 'ngModel',
     link: function(scope, element, attrs, modelCtrl) {
       modelCtrl.$parsers.push(function (inputValue) {
           if (inputValue == undefined) return ''
           var transformedInput = inputValue.replace(/[^0-9]/g, '');
           if (transformedInput!=inputValue) {
              modelCtrl.$setViewValue(transformedInput);
              modelCtrl.$render();
           }

           return transformedInput;
       });
     }
   };
}).directive('autocomplete', function(){
  var index = -1;

  return {
    restrict: 'E',
    scope: {
      searchParam: '=ngModel',
      suggestions: '=data',
      onType: '=onType'
    },
    controller: function($scope, $element, $attrs){
      $scope.searchParam;

      // with the searchFilter the suggestions get filtered
      $scope.searchFilter;

      // the index of the suggestions that's currently selected
      $scope.selectedIndex = -1;

      // set new index
      $scope.setIndex = function(i){
        $scope.selectedIndex = parseInt(i);
      }

      this.setIndex = function(i){
        $scope.setIndex(i);
        $scope.$apply();
      }

      $scope.getIndex = function(i){
        return $scope.selectedIndex;
      }

      // watches if the parameter filter should be changed
      var watching = true;

      // autocompleting drop down on/off
      $scope.completing = false;

      // starts autocompleting on typing in something
      $scope.$watch('searchParam', function(newValue, oldValue){
        if (oldValue === newValue) {
          return;
        }

        if(watching && $scope.searchParam) {
          $scope.completing = true;
          $scope.searchFilter = $scope.searchParam;
          $scope.selectedIndex = -1;
        }

        // function thats passed to on-type attribute gets executed
        if($scope.onType)
          $scope.onType($scope.searchParam);
      });

      // for hovering over suggestions
      this.preSelect = function(suggestion){

        watching = false;

        // this line determines if it is shown 
        // in the input field before it's selected:
        //$scope.searchParam = suggestion;

        $scope.$apply();
        watching = true;

      }

      $scope.preSelect = this.preSelect;

      this.preSelectOff = function(){
        watching = true;
      }

      $scope.preSelectOff = this.preSelectOff;

      // selecting a suggestion with RIGHT ARROW or ENTER
      $scope.select = function(suggestion){
        if(suggestion){
          $scope.searchParam = suggestion;
          $scope.searchFilter = suggestion;
          // $scope.editRule.publicPort  = $scope.editRule.commonPort.port;
          // $scope.editRule.localPort = $scope.editRule.commonPort.port;
          // console.log($scope.editRule);
          // $scope.editRule.localPort = "";
          // $scope.editRule.localPort = suggestion;
          // alert(/////////////);
          // $scope.editRule.commonPort = 2;
          // consol.log($scope.editRule.commonPort);
          // $scope.editRule.commonPort = suggestion;
          $scope.commonPortVar = $scope.searchParam;
          console.log($scope.commonPortVar);
        }
        watching = false;
        $scope.completing = false;
        setTimeout(function(){watching = true;},1000);
        $scope.setIndex(-1);

      }


    },
    link: function(scope, element, attrs){

      var attr = '';

      // Default atts
      scope.attrs = {
        "placeholder": "",
        "class": "",
        "id": "",
        "inputclass": "",
        "inputid": ""
      };

      for (var a in attrs) {
        attr = a.replace('attr', '').toLowerCase();
        // add attribute overriding defaults
        // and preventing duplication
        if (a.indexOf('attr') === 0) {
          scope.attrs[attr] = attrs[a];
        }
      }

      if(attrs["clickActivation"]=="true"){
        element[0].onclick = function(e){
          if(!scope.searchParam){
            scope.completing = true;
            scope.$apply();
          }
        };
      }

      var key = {left: 37, up: 38, right: 39, down: 40 , enter: 13, esc: 27};

      document.addEventListener("keydown", function(e){
        var keycode = e.keyCode || e.which;

        switch (keycode){
          case key.esc:
            // disable suggestions on escape
            scope.select();
            scope.setIndex(-1);
            scope.$apply();
            e.preventDefault();
        }
      }, true);
      
      document.addEventListener("blur", function(e){
        // disable suggestions on blur
        // we do a timeout to prevent hiding it before a click event is registered
        setTimeout(function() {
          scope.select();
          scope.setIndex(-1);
          scope.$apply();
        }, 200);
      }, true);

      element[0].addEventListener("keydown",function (e){
        var keycode = e.keyCode || e.which;

        var l = angular.element(this).find('li').length;

        // implementation of the up and down movement in the list of suggestions
        switch (keycode){
          case key.up:    
 
            index = scope.getIndex()-1;
            if(index<-1){
              index = l-1;
            } else if (index >= l ){
              index = -1;
              scope.setIndex(index);
              scope.preSelectOff();
              break;
            }
            scope.setIndex(index);

            if(index!==-1)
              scope.preSelect(angular.element(angular.element(this).find('li')[index]).text());

            scope.$apply();

            break;
          case key.down:
            index = scope.getIndex()+1;
            if(index<-1){
              index = l-1;
            } else if (index >= l ){
              index = -1;
              scope.setIndex(index);
              scope.preSelectOff();
              scope.$apply();
              break;
            }
            scope.setIndex(index);
            
            if(index!==-1)
              scope.preSelect(angular.element(angular.element(this).find('li')[index]).text());

            break;
          case key.left:    
            break;
          case key.right:  
          case key.enter:  

            index = scope.getIndex();
            // scope.preSelectOff();
            if(index !== -1)
              scope.select(angular.element(angular.element(this).find('li')[index]).text());
            scope.setIndex(-1);     
            scope.$apply();

            break;
          case key.esc:
            // disable suggestions on escape
            scope.select();
            scope.setIndex(-1);
            scope.$apply();
            e.preventDefault();
            break;
          default:
            return;
        }

        if(scope.getIndex()!==-1 || keycode == key.enter)
          e.preventDefault();
      });
    },
    template: '<div class="autocomplete {{attrs.class}}" id="{{attrs.id}}">'+
                '<input type="text" ng-model="searchParam" placeholder="{{attrs.placeholder}}" class="form-control" id="{{attrs.inputid}}" style="width: 173px;"/>' +
                '<ul ng-show="completing">' +
                  '<li suggestion ng-repeat="suggestion in suggestions | filter:searchFilter | orderBy:\'toString()\' track by $index"'+
                  'index="{{$index}}" val="{{suggestion.port}}" ng-class="{active: '+
                  '($index == selectedIndex)}" ng-click="select(suggestion.port)" '+
                  'ng-bind-html="suggestion | highlight:searchParam">'+
                    '{{suggestion.name}} / {{suggestion.port}}' +
                  '</li>'+
                '</ul>'+
              '</div>'
    // templateUrl: 'script/ac_template.html'
  }
}).filter('highlight', function ($sce) {

  return function (input, searchParam) {

    if (searchParam) {
      var words = searchParam.split(/\ /).join('|'),
          exp = new RegExp("(" + words + ")", "gi");

      if (words.length) {
        //////////////////
        // input = $sce.trustAsHtml(input.replace(exp, "<span class=\"highlight\">$1</span>")); 
      }
    }

    return input;

  }

}).directive('suggestion', function(){
  return {
    restrict: 'A',
    require: '^autocomplete', // ^look for controller on parents element
    link: function(scope, element, attrs, autoCtrl){
      element.bind('mouseenter', function() {
        autoCtrl.preSelect(attrs['val']);
        autoCtrl.setIndex(attrs['index']);
      });

      element.bind('mouseleave', function() {
        autoCtrl.preSelectOff();
      });
    }
  }
});
