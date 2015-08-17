module.exports = function(config) {
  config.set({
    basePath: '',
    frameworks: ['mocha', 'chai'],
    files: [
      'static/bower_components/angular/angular.js',
      'static/bower_components/angular-route/angular-route.js',

      'node_modules/angular-mocks/angular-mocks.js',

      'static/app.js',
    ],
    preprocessors: {
      'static/app.js' : ['coverage'],
      'static/**/*.html' : ['ng-html2js'],
    },
    ngHtml2JsPreprocessor: {
      stripPrefix: 'static/',
      moduleName: 'testTemplates',
    },
    reporters: ['progress', 'coverage'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: false,
    browsers: ['PhantomJS'],
    singleRun: true,
  });
};
