'use strict';

angular.module('cloudscalers.directives', []);

function resizeIFrame() {
    var element = angular.element('iframe')[0];

    element.width = element.contentWindow.document.body.scrollWidth
    element.height = element.contentWindow.document.body.scrollHeight;
};