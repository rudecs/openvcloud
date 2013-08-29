'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers'])
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/list', {templateUrl: 'partials/list', controller: 'BucketListCtrl'});
        $routeProvider.when('/new', {templateUrl: 'partials/new', controller: 'BucketNewCtrl'});
        //$routeProvider.when('/edit', {templateUrl: 'partials/edit', controller: 'BucketEditCtrl'});
        $routeProvider.otherwise({redirectTo: '/list'});
    }])
    // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax. Here I configure
    // Angular to use {[]} instead.
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }]);

jQuery(function() {
// UI stuff which are not related to angular
// Popups
    $('.popup-show').on('click', function(e) {
        e.preventDefault();
        $($(this).attr('href')).toggle('fast');
    });
    $('.popup-background').on('click', function() {
        $(this).parent().hide();
    });
    $('.popup-content').on('click', function(e) {
        e.stopPropagation();
    });

    // When radio buttons inside li.shortcut is selected, make the whole li selected, for better UI
    function selectParent() {
        var btn = $(this);
        btn.parents('.shortcuts').find('li.shortcut').removeClass('selected');
        if (btn.attr('checked'))
            btn.parents('.shortcut').addClass('selected');
    };
    $('.shortcut > input[type=radio]').on('change', selectParent);
    $('.shortcut > input[type=radio]:checked').each(selectParent);

    // Context-menu on buckets list
    $.contextMenu({
        selector: '#machine_buckets_list > tbody > tr', 
        build: function($trigger, e) {
            var bucket = ko.dataFor(e.srcElement);
            var startOrStop = bucket.status() == 'off' ? 'start': 'stop';
            return {
                callback: function(key, options) {
                    if (key === 'startOrStop') {
                        if (bucket.status() == 'off')
                            bucket.status('active');
                        else
                            bucket.status('off');
                    } else if (key === 'edit') {
                        location.href = bucket.bucketUrl();
                    } else if (key == 'destroy') {
                        bucket.destroy();
                    }
                },
                items: {
                    startOrStop: {name: startOrStop[0].toUpperCase() + startOrStop.substr(1).toLowerCase()},
                    "edit": {name: "Edit"},
                    "monitoring": {name: "Monitoring"},
                    "rename": {name: "Rename"},
                    "create snapshot": {name: "Create snapshot"},
                    "destroy": {name: "Destroy"}
                }
            };
        }
    });
});