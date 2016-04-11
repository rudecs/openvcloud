'use strict';

angular.module('cloudscalers.directives', [])
.directive('novncwindow', function() {
  return {
    restrict: 'A',
    link: function(scope, elem, attrs) {
      scope.showPlaceholder = false;
      var updateState = function(rfb, state) {
        var s;
        var cad;
        var level;
        s = $D('noVNC_status');
        cad = $D('sendCtrlAltDelButton');
        switch (state) {
          case 'failed': level = 'error'; break;
          case 'fatal': level = 'error'; break;
          case 'normal': level = 'normal'; break;
          case 'disconnected': level = 'normal'; break;
          case 'loaded': level = 'normal'; break;
          default: level = 'warn'; break;
        }

        if (state === 'normal') {
          cad.disabled = false;
          $D('capturekeyboardbutton').disabled = false;
        } else {
          cad.disabled = true;
          $D('capturekeyboardbutton').disabled = true;
        }
      };

      var connect = function() {
        if (scope.rfb) {return;}
        scope.showPlaceholder = false;
        var rfb = new RFB({'target': $D('noVNC_canvas'),
                     'encrypt': window.location.protocol === 'https:',
                     'repeaterID': '',
                     'true_color': true,
                     'local_cursor': false,
                     'shared': true,
                     'view_only': false,
                     'updateState': updateState
                     });
        rfb.connect(scope.connectioninfo.host, scope.connectioninfo.port, '', scope.connectioninfo.path);
        scope.rfb = rfb;
      };

      var disconnect = function() {
        if (scope.rfb) {
          scope.rfb.disconnect();
          scope.rfb.get_keyboard().set_focused(false);
          delete(scope.rfb);
        }
        scope.showPlaceholder = true;
      };

      scope.$watch(attrs.connectioninfo, function(newValue) {
        if (newValue && newValue.host) {
          scope.connectioninfo = newValue;
          connect();
        } else {
          disconnect();
        }
      }, true);

    },
    template: '<div id="noVNC_status_bar" class="noVNC_status_bar" ng-show="!showPlaceholder">' +
                '<table border=0><tr>' +
                '<td><div id="noVNC_status" style="position: relative; height: auto;">' +
                '</div></td>' +
                '<td>' +
                '</td>' +
                '</tr></table>' +
              '<canvas id="noVNC_canvas" width="640px" height="20px">' +
                'Canvas not supported.' +
              '</canvas>' +
              '</div>' +
              '<div class="margin-left-medium" ng-show="showPlaceholder">' +
              'A machine must be started to access the console!</div>'
  };
}).directive('persistentDropdown', function() {
  return {
    restrict: 'A',
    link: function(scope, element) {
      element.addClass('dropdown-menu').on('click', '.accordion-heading', function(e) {
        // Prevent the click event from propagation to the dropdown & closing it
        e.preventDefault();
        e.stopPropagation();

        // If the body will be expanded, then add .open to the header
        var header = angular.element(this);
        var body = header.siblings('.accordion-body');
        if (body.height() === 0) { // body is collapsed & will be expanded
          header.addClass('open');
        } else {
          header.removeClass('open');
        }
      });
    }
  };
}).directive('expandBasedOnHash', function($window) {
  return {
    restrict: 'A',
    link: function(scope, element) {
      var selection = $window.location.hash.replace('#', '').replace('/', '');
      if (element.attr('id') === selection) {
        // Expand it
        element.addClass('in').css('height', 'auto');
        // Scroll to show it
        element.parents('body').animate({scrollTop: element.siblings('.accordion-heading').offset().top});
      }
    }
  };
}).directive('autofocus', function() {
  return {
    restrict: 'A',
    link: function(scope, element) {
      element.focus();
    }
  };
}).directive('menuLinkActiveLocation',function($window) {
  return {
    restrict: 'A',
    scope: {},
    link: function(scope, element, attrs) {
      var currentlocation = $window.location;
      if (currentlocation.toString().search(attrs.menuLinkActiveLocation) > -1) {
        element.addClass('active');
        element.parents('ul.body')[0].classList.add('active');
      }
    }
  };
}).directive('numbersOnly', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, modelCtrl) {
       modelCtrl.$parsers.push(function(inputValue) {
         if (inputValue === undefined) { return '';}
         var transformedInput = inputValue.replace(/[^0-9]/g, '');
         if (transformedInput !== inputValue) {
           modelCtrl.$setViewValue(transformedInput);
           modelCtrl.$render();
         }

         return transformedInput;
       });
     }
  };
}).directive('autocomplete', function() {
  var index = -1;
  return {
    restrict: 'E',
    scope: {
      searchParam: '=ngModel',
      suggestions: '=data',
      onType: '=onType'
    },
    controller: function($scope) {
      $scope.selectedIndex = -1;
      $scope.setIndex = function(i) {
        $scope.selectedIndex = parseInt(i);
      };
      this.setIndex = function(i) {
        $scope.setIndex(i);
        $scope.$apply();
      };
      $scope.getIndex = function() {
        return $scope.selectedIndex;
      };
      var watching = true;
      $scope.completing = false;
      $scope.$watch('searchParam', function(newValue, oldValue) {
        if (oldValue === newValue) {
          return;
        }

        if (watching && $scope.searchParam) {
          $scope.completing = true;
          $scope.searchFilter = $scope.searchParam;
          $scope.selectedIndex = -1;
        }
        if ($scope.onType) {
          $scope.onType($scope.searchParam);
        }
      });
      this.preSelect = function() {
        watching = false;
        $scope.$apply();
        watching = true;
      };

      $scope.preSelect = this.preSelect;

      this.preSelectOff = function() {
        watching = true;
      };

      $scope.preSelectOff = this.preSelectOff;

      $scope.select = function(suggestion) {
        if (suggestion) {
          $scope.searchParam = suggestion;
          $scope.searchFilter = suggestion;

        } else {
          $scope.searchFilter = '';
        }
        watching = false;
        $scope.completing = false;
        setTimeout(function() {watching = true;},1000);
        $scope.setIndex(-1);

      };

    },
    link: function(scope, element, attrs) {

      var attr = '';

      // Default atts
      scope.attrs = {
        'placeholder': 'Port',
        'class': '',
        'id': '',
        'inputclass': '',
        'inputid': ''
      };

      for (var a in attrs) {
        attr = a.replace('attr', '').toLowerCase();
        if (a.indexOf('attr') === 0) {
          scope.attrs[attr] = attrs[a];
        }
      }

      if (attrs['clickActivation'] === 'true') {
        element[0].onclick = function() {
          if (!scope.searchParam) {
            scope.completing = true;
            scope.$apply();
          } else {
            scope.completing = true;
            scope.$apply();
          }
        };
      }

      var key = {left: 37, up: 38, right: 39, down: 40 , enter: 13, esc: 27};

      document.addEventListener('keydown', function(e) {
        var keycode = e.keyCode || e.which;
        switch (keycode){
          case key.esc:
            scope.select();
            scope.setIndex(-1);
            scope.$apply();
            e.preventDefault();
        }
      }, true);

      element[0].addEventListener('blur', function() {
        setTimeout(function() {
          scope.select();
          scope.setIndex(-1);
          scope.$apply();
        }, 200);
      }, true);

      element[0].addEventListener('keydown',function(e) {

        var keycode = e.keyCode || e.which;
        var l = angular.element(this).find('li').length;
        switch (keycode){
          case key.up:

            index = scope.getIndex() - 1;
            if (index < -1) {
              index = l - 1;
            } else if (index >= l) {
              index = -1;
              scope.setIndex(index);
              scope.preSelectOff();
              break;
            }
            scope.setIndex(index);

            if (index !== -1) {
              scope.preSelect(
                angular.element(angular.element(this).find('li')[index]).text()
              );
            }
            scope.$apply();

            break;
          case key.down:

            index = scope.getIndex() + 1;
            if (index < -1) {
              index = l - 1;
            } else if (index >= l) {
              index = -1;
              scope.setIndex(index);
              scope.preSelectOff();
              scope.$apply();
              break;
            }
            scope.setIndex(index);

            if (index !== -1) {
              scope.preSelect(
                angular.element(angular.element(this).find('li')[index]).text()
              );
            }

            break;
          case key.left:
            break;
          case key.right:
          case key.enter:

            index = scope.getIndex();
            if (index !== -1) {
              scope.select(
                angular.element(
                  angular.element(this).find('li')[index]
                ).context.attributes.val.value
              );
            }
            scope.setIndex(-1);
            scope.$apply();

            break;
          case key.esc:
            scope.select();
            scope.setIndex(-1);
            scope.$apply();
            e.preventDefault();
            break;
          default:
            return;
        }

        if (scope.getIndex() !== -1 || keycode === key.enter) { e.preventDefault(); }
      });
    },
    template: '<div class="autocomplete {{attrs.class}}" id="{{attrs.id}}">' +
                '<input type="text" ng-model="searchParam" required numbers-only="numbers-only"' +
                ' placeholder="{{attrs.placeholder}}" class="form-control" id="{{attrs.inputid}}"' +
                ' style="width: 173px; position:relative;"></input>' +
                '<ul ng-show="completing">' +
                  '<li suggestion ng-repeat="suggestion in suggestions | filter:searchFilter |' +
                  ' orderBy:\'toString()\' track by $index"' +
                  'index="{{$index}}" val="{{suggestion.port}}" ng-class="{active: ' +
                  '($index === selectedIndex)}" ng-click="select(suggestion.port)"> ' +
                    '{{suggestion.name}} / {{suggestion.port}}' +
                  '</li>' +
                '</ul>' +
              '</div>'
  };
}).directive('suggestion', function() {
  return {
    restrict: 'A',
    require: '^autocomplete', // ^look for controller on parents element
    link: function(scope, element, attrs, autoCtrl) {
      element.bind('mouseenter', function() {
        autoCtrl.preSelect(attrs['val']);
        autoCtrl.setIndex(attrs['index']);
      });
      element.bind('mouseleave', function() {
        autoCtrl.preSelectOff();
      });
    }
  };
});
