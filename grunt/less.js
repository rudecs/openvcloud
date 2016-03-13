module.exports = function(grunt, config) {
  return {
    options: {
      outputSourceFiles: true,
      dumpLineNumbers: 'all'
    },
    all: {
      files: {
        'apps/ms1_fe/base/wiki_gcb/.files/css/custom.css': 'apps/ms1_fe/base/wiki_gcb/.files/less/custom.less'
      }
    }
  };
};
