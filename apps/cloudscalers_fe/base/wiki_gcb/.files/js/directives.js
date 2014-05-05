'use strict';

angular.module('cloudscalers.directives', [])
	.directive('novncwindow', function(){
	    return {
	        restrict: 'A',
	        link: function (scope, elem, attrs) {
                scope.showPlaceholder = false;
                var updateState = function(rfb, state, oldstate, msg) {
            			var s, sb, cad, level;
            			s = $D('noVNC_status');
            			cad = $D('sendCtrlAltDelButton');
            			switch (state) {
                			case 'failed':       level = "error";  break;
                			case 'fatal':        level = "error";  break;
                			case 'normal':       level = "normal"; break;
                			case 'disconnected': level = "normal"; break;
                			case 'loaded':       level = "normal"; break;
                			default:             level = "warn";   break;
            			}

            			if (state === "normal") { cad.disabled = false;$D('capturekeyboardbutton').disabled = false; }
            			else                    { cad.disabled = true; $D('capturekeyboardbutton').disabled = true;}

        		};



        		var connect = function(){
				if (scope.rfb)
					{return;}
				scope.showPlaceholder = false;
        			var rfb = new RFB({'target': $D('noVNC_canvas'),
                           'encrypt': window.location.protocol === "https:",
                           'repeaterID': '',
                           'true_color': true,
                           'local_cursor': false,
                           'shared':       true,
                           'view_only':    false,
                           'updateState':  updateState,
                           });
            		rfb.connect(window.location.host, scope.connectioninfo.port, '', scope.connectioninfo.path);
            		scope.rfb = rfb;
    			}

			var disconnect = function(){
                       		if (scope.rfb){
		            		scope.rfb.disconnect();
                            		scope.rfb.get_keyboard().set_focused(false);
			    		delete(scope.rfb);
				}
				scope.showPlaceholder = true;
			}

        		scope.$watch(attrs.connectioninfo, function(newValue, oldValue) {
	                    	if (newValue && newValue.host) {
        	                	scope.connectioninfo = newValue;
					connect();
                    		}
                    		else {
					disconnect();
        			}
			}, true);


	        },
		template: '<div id="noVNC_status_bar" class="noVNC_status_bar" ng-show="!showPlaceholder">\
                        <table border=0><tr>\
                        <td><div id="noVNC_status" style="position: relative; height: auto;">\
                        </div></td>\
                        <td>\
                        </td>\
                        </tr></table>\
                    <canvas id="noVNC_canvas" width="640px" height="20px">\
                        Canvas not supported.\
                    </canvas>\
                    </div>\
                    <div class="mlm" ng-show="showPlaceholder">A machine must be started to access the console!</div>\
                    ',
	     }
	})

    .directive('persistentDropdown', function() {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                element.addClass('dropdown-menu').on('click', '.accordion-heading', function(e) {
                    // Prevent the click event from propagation to the dropdown & closing it
                    e.preventDefault();
                    e.stopPropagation();

                    // If the body will be expanded, then add .open to the header
                    var header = angular.element(this);
                    var body = header.siblings('.accordion-body');
                    if (body.height() === 0) // body is collapsed & will be expanded
                        header.addClass('open');
                    else
                        header.removeClass('open');
                });
            }
        };
    })
    .directive('expandBasedOnHash', function($window, $timeout) {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                var selection = $window.location.hash.replace('#', '').replace('/', '');
                if (element.attr('id') == selection) {
                    // Expand it
                    element.addClass('in').css('height', 'auto');
                    // Scroll to show it
                    element.parents('body').animate({scrollTop: element.siblings('.accordion-heading').offset().top});
                }
            }
        };
    })
    .directive('autofocus', function() {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                element.focus();
            }
        };
    })
		.directive('menuLinkActiveLocation',function($window) {
			return {
				restrict: 'A',
				scope: {},
				link: function(scope, element, attrs) {
					var currentlocation = $window.location;
					if (currentlocation.toString().search(attrs.menuLinkActiveLocation) > -1){
							element.addClass('active');
							element.parents('ul.body')[0].classList.add('active');
						}
				}
			};
		})
;
