'use strict';

angular.module('cloudscalers')
.directive('swaggerUiContainer', function() {
  return {
    restrict: 'A',
    link: function(scope, elem, attrs) {

      var loadAPI = function(api_key) {
        window.swaggerUi = new SwaggerUi({
          url: '/restmachine/system/docgenerator/prepareCatalog?' +
            'actors=cloudapi__machines,cloudapi__accounts,' +
            'cloudapi__cloudspaces,cloudapi__disks,cloudapi__images' +
            ',cloudapi__locations,cloudapi__portforwarding,cloudapi__sizes,' +
            'cloudapi__users&format=jsonraw&skip_private=true',
          validatorUrl: null,
          apiKey: api_key,
          apiKeyName: 'authkey',
          dom_id: 'swagger-ui-container',
          supportHeaderParams: false,
          supportedSubmitMethods: ['get', 'post', 'put'],
          onComplete: function() {
            $('pre code').each(function(i, e) {hljs.highlightBlock(e);});
          },
          onFailure: function(data) {
            if (console) {
              console.log('Unable to Load SwaggerUI');
              console.log(data);
            }
          },
          docExpansion: 'none'
        });

        window.swaggerUi.load();

      };

      scope.$watch(attrs.apiKey, function(newValue) {
        loadAPI(newValue);
      });

    }
  };
})
.directive('persistentDropdown', function() {
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
        if (body.height() === 0) {// body is collapsed & will be expanded
          header.addClass('open');
        } else {
          header.removeClass('open');
        }
      });

      // Keep the left border aligned with the border of the window.
      // Because 'position: absolute' doesn't work inside <ul>, I need to do it with JS.
      setInterval(function() {
        element.css('margin-left', -element.parent('li').offset().left);
      }, 50);
    }
  };
});
