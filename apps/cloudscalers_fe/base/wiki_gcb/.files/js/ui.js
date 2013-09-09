$(function () {
	
	Application.init ();
	
});



var Application = function () {
	
	var validationRules = getValidationRules ();
	
	return { init: init, validationRules: validationRules };
	
	function init () {
		
		enableBackToTop ();
		enableLightbox ();
		enableCirque ();
		enableEnhancedAccordion ();
		enableNavigationHighlight();
		enablePopups();
	}

	function enableCirque () {
		if ($.fn.lightbox) {
			$('.ui-lightbox').lightbox ();
		}
	}

	function enableLightbox () {
		if ($.fn.cirque) {
			$('.ui-cirque').cirque ({  });
		}
	}

	function enableBackToTop () {
		var backToTop = $('<a>', { id: 'back-to-top', href: '#top' });
		var icon = $('<i>', { class: 'icon-chevron-up' });

		backToTop.appendTo ('body');
		icon.appendTo (backToTop);
		
	    backToTop.hide();

	    $(window).scroll(function () {
	        if ($(this).scrollTop() > 150) {
	            backToTop.fadeIn ();
	        } else {
	            backToTop.fadeOut ();
	        }
	    });

	    backToTop.click (function (e) {
	    	e.preventDefault ();

	        $('body, html').animate({
	            scrollTop: 0
	        }, 600);
	    });
	}
	
	function enableEnhancedAccordion () {
		$('.accordion').on('show', function (e) {
	         $(e.target).prev('.accordion-heading').parent ().addClass('open');
	    });
	
	    $('.accordion').on('hide', function (e) {
	        $(this).find('.accordion-toggle').not($(e.target)).parents ('.accordion-group').removeClass('open');
	    });
	    
	    $('.accordion').each (function () {	    	
	    	$(this).find ('.accordion-body.in').parent ().addClass ('open');
	    });
	}
	
	function getValidationRules () {
		var custom = {
	    	focusCleanup: false,
			
			wrapper: 'div',
			errorElement: 'span',
			
			highlight: function(element) {
				$(element).parents ('.control-group').removeClass ('success').addClass('error');
			},
			success: function(element) {
				$(element).parents ('.control-group').removeClass ('error').addClass('success');
				$(element).parents ('.controls:not(:has(.clean))').find ('div:last').before ('<div class="clean"></div>');
			},
			errorPlacement: function(error, element) {
				error.appendTo(element.parents ('.controls'));
			}
	    	
	    };
	    
	    return custom;
	}

	function enableNavigationHighlight() {
		var href = window.location.href;
	    var parts = href.split("/");
	    $(".sidebar-nav li.active a").parent().removeClass("active");
	    $(".sidebar-nav li:has(a[href$='"+ decodeURIComponent(parts[parts.length -1]) +"'])").addClass("active");
	    $(".mainnav li.active a").parent().removeClass("active");
	    $(".mainnav li:has(a[href$='"+ decodeURIComponent(parts[parts.length -1]) +"'])").addClass("active");
	}

	function enablePopups() {
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
	}
	
}();


function getFormattedDate() {
    var d = new Date();
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDay() + " " + d.getHours() + ":" + d.getMinutes();
}

function showLoading() {
    $('#create-ssh').show('fast');
    setTimeout(function() {
        $('#create-ssh').hide('fast');
    }, 3000);
}