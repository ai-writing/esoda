/*
* Logic for esoda result page.
*/

var loadCount = 1, loading = 0, loaded = 0;    // TODO: eliminate global vairables
var keyword = window.location.search;

$(function () {
  'use strict';

  // if( keyword.indexOf("&") >= 0) {    // TODO @xiaofei: should not test by words used in example
  //   $(".cover").show();
  //   if( keyword.indexOf("efficient") >= 0) {
  //     $(".uncover-syn .uncover").css('z-index','1500');
  //   }
  //   if( keyword.indexOf("wait") >= 0) {
  //     $(".uncover-colloc .uncover").css('z-index','1500');
  //   }
  //   if( keyword.indexOf("demand") >= 0) {
  //     $(".uncover-chi .uncover").css('z-index','1500');
  //   }
  //   if( keyword.indexOf("effort") >= 0) {
  //     $(".uncover-phrase .uncover").css('z-index','1500');
  //   }
  // }

  // $(".cover").click( function() {
  //   $(".cover").hide();
  //   $(".uncover").css('z-index','0'); 
  // });

  // $( window ).scroll( function () {
  //   if ($(document).height() <= $(window).scrollTop() + $(window).height() + 300) {
  //     if (loading == 1 || loaded == 1 ) return;
  //     if ($('#Loading').is(':visible')) return;

  //     var total = $("#ExampleNumber").html();
  //     loading = 1;
  //     $("#Loading").show();
  //     setTimeout(function() {
  //       $("#Loading").hide();
  //       var i;
  //       for (i = loadCount * 10 + 1; i <= (loadCount + 1) * 10 && i <= total; i++) {
  //         $("#Example" + i).show();
  //       }
  //       loadCount++;
  //       loading = 0;
  //       if (i > total || loadCount >= 5) {
  //         loaded = 1;
  //         $("#ExampleEnd").show();
  //         return;
  //       }
  //     }, 1000);
  //   }
  // });
  
  
$( window ).scroll( function () {
  if ($(document).height() <= $(window).scrollTop() + $(window).height() + 300) {
    if (loading == 1 || loaded == 1 ) return;
    if ($('#Loading').is(':visible')) return;
    if ($('#ManualLoad').is(':visible')) return;
    $("#ManualLoad").show();
  }; 
});

$('#ManualLoad').click(function(e) {
    var total = $("#ExampleNumber").html();
    loading = 1;
    $("#ManualLoad").hide();
    $("#Loading").show();
    setTimeout(function() {
      $("#Loading").hide();
      var i;
      for (i = loadCount * 10 + 1; i <= (loadCount + 1) * 10 && i <= total; i++) {
        $("#Example" + i).show();
      }
      loadCount++;
      loading = 0;
      if (i > total || loadCount >= 5) {
        loaded = 1;
        $("#ExampleEnd").show();
        return;
      }
    }, 1000);
  });

  $(".back-to-top").click(function() {
    $("html,body").animate({scrollTop: 0}, "fast");
    return false;
  });

  $("#SidebarAffix").affix({
    offset: {
      top: 20,
      bottom: function () {
        return $(".footer").outerHeight(true) + $("#BackToTopAffix").outerHeight(true) + 40;
      }
    }
  });

  $("#BackToTopAffix").affix({
    offset: {
      top: 0,
      bottom: function () {
        // TODO: fix position bugs on change of window length
        return $(".footer").outerHeight(true) + 20;
      }
    }
  });

  $.clickStar = function(e) {
    e.preventDefault();
    $(e.target).toggleClass("glyphicon-star-empty");
    $(e.target).toggleClass("glyphicon-star");
  };

  $.clickChevron = function(e) {    // TODO: No need of this function, collpase.js will automatically handle
    $(e.target).toggleClass("glyphicon-chevron-down");
    $(e.target).toggleClass("glyphicon-chevron-up");
  }

  $('#SearchBox').hover(function() {
    if ($('#SearchBox').is(':focus')) {
      return false;
    }
    $('#SearchBox').focus();
    $('#SearchBox').select();
  }, function() {
    return false;
  });

  $('#SearchBox').trigger('mouseover');
});
