(function ($) {
  'use strict';

  // Main function
  $.contactButtons = function( options ){
    
    // Define the defaults
    var defaults = { 
      effect  : '', // slide-on-scroll
      buttons : {
        'facebook':   { class: 'facebook',  use: false, icon: 'facebook',    link: '', title: 'Follow on Facebook' },
        'skype':   { class: 'skype',  use: false, icon: 'skype',    link: '', title: 'Follow on Skype' },
        'youtube':   { class: 'youtube',  use: false, icon: 'youtube',    link: '', title: 'Follow on Youtube' },
        'instagram':   { class: 'instagram',  use: false, icon: 'instagram',    link: '', title: 'Follow on Instagram' },
        //'google':     { class: 'gplus',     use: false, icon: 'google-plus', link: '', title: 'Visit on Google Plus' },
        'linkedin':   { class: 'linkedin',  use: false, icon: 'linkedin',    link: '', title: 'Visit on LinkedIn' },
        'twitter':    { class: 'twitter',   use: false, icon: 'twitter',     link: '', title: 'Follow on Twitter' },
        'tumblr':   { class: 'tumblr',  use: false, icon: 'tumblr',    link: '', title: 'Follow on Tumblr' },
        //'pinterest':  { class: 'pinterest', use: false, icon: 'pinterest',   link: '', title: 'Follow on Pinterest' },
        //'phone':      { class: 'phone',     use: false, icon: 'phone',       link: '', title: 'Call us', type: 'phone' },
        //'email':      { class: 'email',     use: false, icon: 'envelope',    link: '', title: 'Send us an email', type: 'email' }
      }
    };

    // Merge defaults and options
    var s,
        settings = options;
    for (s in defaults.buttons) {
      if (options.buttons[s]) {
        settings.buttons[s] = $.extend( defaults.buttons[s], options.buttons[s] );
      }
    }
    
    // Define the container for the buttons
    var oContainer = $("#contact-buttons-bar");

    // Check if the container is already on the page
    if ( oContainer.length === 0 ) {
      
      // Insert the container element
      $('body').append('<div id="contact-buttons-bar">');
      
      // Get the just inserted element
      oContainer = $("#contact-buttons-bar");
      
      // Add class for effect
      oContainer.addClass(settings.effect);
      
      // Add show/hide button
      var sShowHideBtn = '<button class="contact-button-link show-hide-contact-bar"><span class="fa fa-angle-left"></span></button>';
      oContainer.append(sShowHideBtn);
      
      var i;
      for ( i in settings.buttons ) {
        var bs = settings.buttons[i],
            sLink = bs.link,
            active = bs.use;
        
        // Check if element is active
        if (active) {
          
          // Change the link for phone and email when needed
          if (bs.type === 'phone') {
            sLink = 'tel:' + bs.link;
          } else if (bs.type === 'email') {
            sLink = 'mailto:' + bs.link;
          }
          
          // Insert the links
          var sIcon = '<span class="fa fa-' + bs.icon + '"></span>',
              sButton = '<a href="' + sLink + 
                          '" class="contact-button-link cb-ancor ' + bs.class + '" ' + 
                          (bs.title ? 'title="' + bs.title + '"' : '') + 
                          (bs.extras ? bs.extras : '') + 
                          '>' + sIcon + '</a>';
          oContainer.append(sButton);
        }
      }
      
      // Make the buttons visible
      setTimeout(function(){
        oContainer.animate({ left : 0 });
      }, 200);
      
      // Show/hide buttons
      $('body').on('click', '.show-hide-contact-bar', function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        $('.show-hide-contact-bar').find('.fa').toggleClass('fa-angle-right fa-angle-left');
        oContainer.find('.cb-ancor').toggleClass('cb-hidden');
      });
    }
  };
  
  // Slide on scroll effect
  $(function(){
    
    // Define element to slide
    var el = $("#contact-buttons-bar.slide-on-scroll");
    
    // Load top default
    setTimeout(function(){window.top_ = $("#contact-buttons-bar.slide-on-scroll").css('top')},0); 
    // Listen to scroll
    $(window).scroll(function() {
      clearTimeout( $.data( this, "scrollCheck" ) );
      $.data( this, "scrollCheck", setTimeout(function() {
        var nTop = $(window).scrollTop() + parseInt(window.top_);
        $("#contact-buttons-bar.slide-on-scroll").animate({
          top : nTop
        }, 500);
      }, 250) );
    });
  });
  
 }( jQuery ));

$(document).ready(function(){
    //social media buttons
	var site_url = window.location.href;
	if (site_url.indexOf('myevidyaloka')<=0){
		  // Google Fonts
	    WebFontConfig = {
	      google: { families: [ 'Lato:400,700,300:latin' ] }
	    };
	    // Initialize Share-Buttons
	    /*
	    $.contactButtons({
	      effect  : 'slide-on-scroll',
	      buttons : {
	        'facebook':   { class: 'facebook', use: true, link: 'https://www.facebook.com/eVidyaloka/', extras: 'target="_blank"' },
	        'linkedin':   { class: 'linkedin', use: true, link: 'https://www.linkedin.com/company/evidyaloka-trust', extras: 'target="_blank"' },
	        'skype'  :    { class: 'skype',    use: true, link: 'skype:evidyaloka.helpdesk?call', extras: 'target="_blank"'},
	        'youtube':    { class: 'youtube',  use: true, link: 'https://www.youtube.com/user/eVidyaloka', extras: 'target="_blank"' },
	        'instagram':  { class:'instagram', use: true, link:'https://www.instagram.com/evidyaloka/', extras: 'target="_blank"'},
	        'tumblr':     { class:'tumblr',    use: true, link:'/', extras: 'target="_blank"'},
	        'twitter':    { class:'twitter',   use: true, link:'https://twitter.com/evidyaloka/', extras: 'target="_blank"'}
	        //'google':     { class: 'gplus',    use: true, link: 'https://plus.google.com/myidongoogle' },
	        //'mybutton':   { class: 'git',      use: true, link: 'http://github.com', icon: 'github', title: 'My title for the button' },
	        //'phone':      { class: 'phone separated',    use: true, link: '+000' },
	        //'email':      { class: 'email',    use: true, link: 'test@web.com' }
	      }
	    });
	    */
	}
  
});
