var gulp = require('gulp');
var jshint = require('gulp-jshint');
var recess = require('gulp-recess');
var trimlines = require('gulp-trimlines');

gulp.task('lint', ['jshint', 'recess'], function() {});

gulp.task('jshint', function() {
  gulp.src(["static/**/*.js", '!static/bower_components/**'])
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});

gulp.task('recess', function() {
  var options = {
    strictPropertyOrder: false,
  };
  gulp.src(["static/**/*.less", '!static/bower_components/**'])
    .pipe(recess(options))
    .pipe(recess.reporter());
});

gulp.task('trimlines', function() {
  var options = {
    leading: false,
  };
  var source = [
    "static/**/*.less",
    "static/**/*.html",
    "static/**/*.js",
    "!static/bower_components/**",
  ];
  gulp.src(source)
    .pipe(trimlines(options))
    .pipe(gulp.dest("static"));
});
