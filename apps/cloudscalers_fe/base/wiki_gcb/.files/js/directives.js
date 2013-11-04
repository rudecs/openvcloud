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
        		    connect(newValue);
        		}, true);
			

	        },
		template: '<div id="noVNC_status_bar" class="noVNC_status_bar" style="margin-top: 0px;">\
                <table border=0 width="100%"><tr>\
<td width="20%">\
<input type=button class="btn" value="Capture keyboard"></input>\
</td>\
                    <td><div id="noVNC_status" style="position: relative; height: auto;">\
                    </div></td>\
                    <td width="1%"><div id="noVNC_buttons">\
                        <input type=button class="btn" ng-click="rfb.sendCtrlAltDel()" value="Send CtrlAltDel"\
                            id="sendCtrlAltDelButton">\
                            </div></td>\
                </tr></table>\
            </div>\
<hr/>\
            <canvas id="noVNC_canvas" width="640px" height="20px">\
                Canvas not supported.\
            </canvas>',
	     }
	})
;
