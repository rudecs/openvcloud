'use strict';

var __lc = {};
__lc.license = 4357241;

// Collapse accordion every time dropdown is shown
$('.dropdown-accordion').on('show.bs.dropdown', function() {
  var accordion = $(this).find($(this).data('accordion'));
  accordion.find('.panel-collapse.in').collapse('hide');
});

// Prevent dropdown to be closed when we click on an accordion link
$('.dropdown-accordion').on('click', 'a[data-toggle="collapse"]', function(event) {
  event.preventDefault();
  event.stopPropagation();
  $($(this).data('parent')).find('.panel-collapse.in').collapse('hide');
  $($(this).attr('href')).collapse('show');
  $(this).parents('.panel-group').find('.panel-heading.open')
  .not($(this).parents('.panel-heading')).removeClass('open');
  $(this).parents('.panel-heading').toggleClass('open');
});

  // (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  // (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  // m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  // })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
  // ga('create', 'UA-47253978-1', 'mothership1.com');
  // ga('send', 'pageview');

