// Karma configuration
// Generated on Mon Sep 02 2013 13:42:46 GMT+0200 (CEST)

module.exports = function(config) {
  config.set({

    // base path, that will be used to resolve files and exclude
    basePath: '../..',


    // frameworks to use
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'test/unit/files/lib/jquery/jquery-latest.js',
      'lib/underscore/underscore-min.js',
      'lib/URI.js',
      'lib/angular-1.2.0/angular.js',
      'lib/angular-1.2.0/angular-route.js',
      'lib/angular-1.2.0/angular-resource.js',
      'lib/angular-1.2.0/angular-mocks.js',
      'lib/numeral/numeral.min.js',
      'lib/angular-ui/ui-bootstrap-tpls-0.6.0.js',
      'lib/angular-ui/slider.min.js',
      'test/unit/config.js',
      'test/unit/apiStub.js',
      'test/unit/cloudscalersmodules.js',
      'js/**/*.js',
      'test/unit/files/js/lib/**/*.js',
      'test/unit/files/js/controllers/**/*.js',
      'test/unit/files/js/services/**/*.js',
    ],


    // list of files to exclude
    exclude: [
      'js/config.js',
      'js/app.js',
      'js/app_anonymous.js'
    ],


    // test results reporter to use
    // possible values: 'dots', 'progress', 'junit', 'growl', 'coverage'
    //reporters: ['progress'],
    reporters: ['coverage', 'progress'],
    coverageReporter: {
      type : 'html',
      dir : 'coverage/'
    },

    preprocessors: {
      'js/directives.js': 'coverage',
      
      'js/services/machineServices.js': 'coverage',
      'js/services/AccountServices.js': 'coverage',
      'js/services/SessionServices.js': 'coverage',
      'js/services/CloudSpaceServices.js': 'coverage',
      'js/services/machineServices.js': 'coverage',

      'js/controllers/MachineBuckets/ConsoleController.js': 'coverage',
      'js/controllers/MachineBuckets/MachineController.js': 'coverage',
      'js/controllers/MachineBuckets/MachineCreationController.js': 'coverage',
      'js/controllers/MachineBuckets/MachineEditController.js': 'coverage',
      'js/controllers/MachineBuckets/MachinePricingController.js': 'coverage',
      'js/controllers/SignUp/SignUpController.js': 'coverage',
      'js/controllers/AuthenticatedSessionController.js': 'coverage',
      'js/controllers/CloudSpaceNavigatorController.js': 'coverage',
      'js/controllers/SessionController.js': 'coverage',
      'js/controllers/AccountAccessManagementController.js': 'coverage',
    },


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // Start these browsers, currently available:
    // - Chrome
    // - ChromeCanary
    // - Firefox
    // - Opera
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    browsers: ['Chrome'],
    //browsers: ['PhantomJS'],


    // If browser does not capture in given timeout [ms], kill it
    captureTimeout: 60000,


    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false
  });
};
