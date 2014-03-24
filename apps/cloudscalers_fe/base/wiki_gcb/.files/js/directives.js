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



        		var connect = function(data){
        			var rfb = new RFB({'target': $D('noVNC_canvas'),
			   'focusContainer': elem[0], //$D('console'),
                           'encrypt': window.location.protocol === "https:",
                           'repeaterID': '',
                           'true_color': true,
                           'local_cursor': false,
                           'shared':       true,
                           'view_only':    false,
                           'updateState':  updateState,
                           });
            		rfb.connect(data.host, data.port, '', data.path);
            		scope.rfb = rfb;
    			}
        
        		scope.$watch(attrs.connectioninfo, function(newValue, oldValue) {
                    if (newValue && newValue.host) {
                        connect(newValue);
                        scope.showPlaceholder = false;
                    }
                    else
                        scope.showPlaceholder = true;
        		}, true);
			

	        },
		template: '<div id="noVNC_status_bar" class="noVNC_status_bar" style="margin-top: 0px;" ng-show="!showPlaceholder">\
                        <table border=0 width="100%"><tr>\
                        <td width="20%">\
                            <input id="capturekeyboardbutton" type=button class="btn" value="Capture keyboard"></input>\
                        </td>\
                        <td><div id="noVNC_status" style="position: relative; height: auto;">\
                        </div></td>\
                        <td width="1%"><div id="noVNC_buttons">\
                        <input type=button class="btn" ng-click="rfb.sendCtrlAltDel()" value="Send CtrlAltDel"\
                            id="sendCtrlAltDelButton">\
                            </div></td>\
                        </tr></table>\
                    <hr/>\
                    <canvas id="noVNC_canvas" width="640px" height="20px">\
                        Canvas not supported.\
                    </canvas>\
                    </div>\
                    <div class="mlm" ng-show="showPlaceholder">Start Machine!</div>\
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
;
