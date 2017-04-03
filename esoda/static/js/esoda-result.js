/*
* Logic for esoda result page.
*/

$(function () {
	'use strict';

  $("#CollocationTab a").click(function (e) {
    e.preventDefault();
    $(this).tab("show");
  });


  $("#UsageTab a").click(function (e) {
    e.preventDefault();
    $(this).tab("show");
  });


  var loadCount = 1, loading = 0, loaded = 0;

  $( window ).scroll( function () {
    if ($(document).height() <= $(window).scrollTop() + $(window).height() + 30) {
      if (loading == 1 || loaded == 1 || loadCount > 4) return;

      loading = 1;
      $("#Loading").show();
      var obj = $.getData("example");
      setTimeout(function() {
        $("#Loading").hide();
        loading = 0;
        if (obj == null) {
          // failed to load obj
        } else {
          if (obj.ended == 1) {
            loaded = 1;
            $("#ExampleEnd").show();
            return;
          }
          loadCount++;
          if (loadCount == 5) {
            $("#ExampleEnd").show();
          }
          $.appendExampleList( obj.list );
        }
      }, 2000);
    }
  });


  $(".back-to-top").click(function() {
    $("html,body").animate({scrollTop: 0}, "fast");
    return false;
  });

  $("#SidebarAffix").affix({
  	offset: {
	    top: 20,
	    bottom: function () {
	      return (this.bottom = $(".footer").outerHeight(true) + $("#BackToTopAffix").outerHeight(true) + 40)
	    }
	  }
  });

  $("#BackToTopAffix").affix({
  	offset: {
  		top: 0,
	    bottom: function () {
	      return (this.bottom = $(".footer").outerHeight(true) + 20)
	    }
	  }
  });

  $.clickStar = function(e) {
    e.preventDefault();
    $(e.target).toggleClass("glyphicon-star-empty");
    $(e.target).toggleClass("glyphicon-star");
  }

  $.clickChevron = function(e) {
    $(e.target).toggleClass("glyphicon-chevron-up");
    $(e.target).toggleClass("glyphicon-chevron-down");
  }
});