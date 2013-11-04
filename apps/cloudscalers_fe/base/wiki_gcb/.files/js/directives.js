'use strict';

angular.module('cloudscalers.directives', [])
	.directive('novncwindow', function(){
	    return {
	        restrict: 'A',
	        link: function (scope, elem, attrs) {
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

            			if (state === "normal") { cad.disabled = false; }
            			else                    { cad.disabled = true; }

            			if (typeof(msg) !== 'undefined') {
                			s.innerHTML = msg;
            			}
        		};



        		var connect = function(data){
        			var rfb = new RFB({'target': $D('noVNC_canvas'),
                           'encrypt': window.location.protocol === "https:",
                           'repeaterID': '',
                           'true_color': true,
                           'local_cursor': true,
                           'shared':       true,
                           'view_only':    false,
                           'updateState':  updateState,
                           });
            		rfb.connect(data.host, data.port, '', data.path);
            		scope.rfb = rfb;
            		$("#noVNC_screen").mouseout(function() {
            			rfb.get_keyboard().set_focused(false);
            		}).mouseover(function() {
            			rfb.get_keyboard().set_focused(true);
            		});
    			}
        
        		scope.$watch(attrs.connectioninfo, function(newValue, oldValue) {
        		    connect(newValue);
        		}, true);
			

	        },
		template: '<div id="noVNC_status_bar" class="noVNC_status_bar" style="margin-top: 0px;">\
                <table border=0 width="100%"><tr>\
                    <td><div id="noVNC_status" style="position: relative; height: auto;">\
                        Loading\
                    </div></td>\
                    <td width="1%"><div id="noVNC_buttons">\
                        <input type=button class="btn" ng-click="rfb.sendCtrlAltDel()" value="Send CtrlAltDel"\
                            id="sendCtrlAltDelButton">\
                            </div></td>\
                </tr></table>\
            </div>\
            <canvas id="noVNC_canvas" width="640px" height="20px">\
                Canvas not supported.\
            </canvas>',
	     }
	})
;
