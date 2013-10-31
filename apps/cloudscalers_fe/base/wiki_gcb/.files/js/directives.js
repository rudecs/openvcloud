'use strict';

angular.module('cloudscalers.directives', [])
	.directive('novncwindow', function(){
	    return {
	        restrict: 'A',
	        link: function (scope, elem, attrs) {
        		var connect = function(data){
        			elem.empty();
    			}
        
        		scope.$watch(attrs.ngModel, function(newValue, oldValue) {
        		    updateChart(newValue);
        		});

	        }
	     }
	})
;
