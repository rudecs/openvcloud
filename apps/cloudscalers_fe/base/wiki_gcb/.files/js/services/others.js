'use strict';

// Read & write JSON objects from/to localStorage
function LocalStorageService(keyName, Constructor) {
    this.keyName = keyName;

    this.getAll = function() {
        var all = [];
        if (localStorage.getItem(keyName))
            all = angular.fromJson(localStorage.getItem(keyName));
        if (Constructor) {   
            var service = this;
            all = all.map(function(e) { return new Constructor(service, e); });
        }
        return all;
    };

    this.saveAll = function(elements) {
        localStorage.setItem(keyName, angular.toJson(elements));
    };

    this.add = function(element) {
        var elements = this.getAll();
        elements.push(element);
        this.saveAll(elements);
    };

    this.getById = function(id) {
        var elements = this.getAll();
        for(var i = 0; i < elements.length; i++) {
            if (elements[i].id && elements[i].id == id)
                return elements[i];
        }
        return null;
    };

    this.save = function(element) {
        var elements = this.getAll();
        if (elements.length == 0) {
            this.add(element);
            return;
        }
        for(var i = 0; i < elements.length; i++) {
            if (elements[i].id && elements[i].id == element.id) {
                elements[i] = element;
                break;
            }
        }
        this.saveAll(elements);
    };

    this.remove = function(element) {
        var elements = this.getAll();
        elements.splice(elements.indexOf(element), 1);
        this.saveAll(elements);
    }
    return this;
}

angular.module('cloudscalers.services')
    .factory('SettingsService', function($http) {
        return new LocalStorageService('gcb-settings', undefined, $http);
    })
    .factory('DesktopBucketService', function($http) {
        var DesktopBucketService = new LocalStorageService('gcb-desktop-buckets', undefined, $http);

        DesktopBucketService.loadSettings = function() {
            if (localStorage.getItem('gcb-desktop-buckets-settings'))
                return JSON.parse(localStorage.getItem('gcb-desktop-buckets-settings'));
        };
        DesktopBucketService.saveSettings = function(settings) {
            localStorage.setItem('gcb-desktop-buckets-settings', JSON.stringify(settings));
        };
        return DesktopBucketService;
    })
    .factory('DNSService', function($http) {
        return new LocalStorageService('gcb-domains', undefined, $http);
    })
    .factory('LoadingDialog', function($q, $timeout) {
        return {
            show: function(msg) {
                angular.element('.loader h2').text(msg || '');

                angular.element('.loader, .loading').fadeIn('fast');
                return $timeout(function() {
                    angular.element('.loader, .loading').fadeOut('fast');
                }, 1000);
            }
        }
    });

