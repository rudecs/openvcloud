module.exports = function(grunt) {
  return {
    options: {
      outputSourceFiles: true,
      dumpLineNumbers: 'all'
    },
    all: {
      files: {
        '.files/css/custom.css': '.files/less/custom.less'
      }
    }
  };
};