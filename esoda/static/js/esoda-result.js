/*
* Logic for esoda result page.
*/

var loadCount = 1, loading = 0, loaded = 0;    // TODO: eliminate global vairables
var REF, SENTENCES_URL, COLLOCATION_URL;
// var keyword = window.location.search;

$(function () {
  'use strict';

  $("#SidebarAffix").height($(window).height());
  // $("#SidebarAffix").height($(".result-page").height())

  function searchAndFillSentences(params) {
    loadCount = 1;
    loading = 1;
    loaded = 0;
    $.get(SENTENCES_URL, params, function (data) {
      $('#Loading').hide();
      $('#ManualLoad').hide();
      $('#SentenceResult').html(data);
      // $('#SentenceResult').css('visibility', 'visible');
      $('#SentenceResult').animate({opacity: 1});
      var exampleNum = Number($("#ExampleNumber").text());
      if (exampleNum <= 10 && exampleNum > 0) {
        $('#ExampleEnd').show();
        loaded = 1;
      }
      loading = 0;
    });
  }

  var colNum = ($(".colList").width() > 600) ? 4 : 3;
  $('.colList li:lt(' + colNum + ')').show();
  $(window).resize(function () {
    colNum = ($(".colList").width() > 600) ? 4 : 3;
    $('.colList li:lt(' + colNum + ')').show();
    $('.colList li').not(':lt(' + colNum + ')').hide();
  });
  $('#colMore').click(function () {
    $('.colList li').show();
    $('#colMore').hide();
    $('#colLess').show();
  });
  $('#colLess').click(function () {
    $('.colList li').not(':lt(' + colNum + ')').hide();
    $('#colLess').hide();
    $('#colMore').show();
  });

  $('.CollapseColloc').on('click', '.colloc-usage', function (e) {
    e.preventDefault();
    if ($(this).attr('state') == 'selected') return;
    $("#ExampleEnd").hide();
    $('#ManualLoad').hide();
    // $('#SentenceResult').css('visibility', 'hidden');
    $('#SentenceResult').animate({opacity: 0}, function () {
      if (loading) $('#Loading').show();
    });

    $('.colloc-usage').removeAttr('state');
    $(this).attr('state', 'selected');

    // var collocQ = $(this).text().split(' ')[0].replace('...', ' ');
    var dt = $(this).parents('.tab-pane').attr('id').split('_')[1];
    var type = $(this).attr('lemma').replace(/ \(.*\)/, '');
    var i = type.replace('...', ' ... ').split(' ').indexOf('...') - 1;
    searchAndFillSentences({t: $(this).attr('lemma'), ref: $(this).attr('ref'), i: i, dt: dt});  // TODO: move to after animation
  });

  // $('.not-limited').click(function (e) {
  //   e.preventDefault();
  //   if ($(this).attr('aria-expanded') == 'true') {
  //     return;
  //   }
  //   $("#ExampleEnd").hide();
  //   $("#ManualLoad").hide();
  //   $('#SentenceResult').empty();
  //   $('#Loading').show();

  //   var query = $(this).attr('data');

  //   searchAndFillSentences({t: query, ref: REF, dt: 0});
  // });

  // $('.not-limited').click();

  $('.colloc-sub-btn').click(function (e) {
    e.preventDefault();
    if ($(this).attr('aria-expanded') == 'true') {
      return;
    }
    var id = $(this).attr('href');
    var type = $(this).attr('type');
    var type0 = type.replace(/ \(.*\) /g, ' ');
    var i, dt;
    var ref = [];
    for (i = 0; i < type.split(' ').length; i++) {
      if (type.split(' ')[i] != type0.split(' ')[i]) break;
    }
    for (var j = 0, k = 0; j < type0.split(' ').length; j++) {
      if (type0.split(' ')[j] == '*') ref[j] = '*';
      else {
        ref[j] = REF.split(' ')[k];
        k = k + 1;
      }
    }
    if (i == 0) i = 1;
    dt = id.replace('#', '').split('_')[1];

    // $('#SentenceResult').css('visibility', 'hidden');

    // $('#SentenceResult').animate({ opacity: 0 }, function () {
    //   $('#Loading').show();
    // });
    // $('#ManualLoad').hide();
    // $("#ExampleEnd").hide();

    $.get(COLLOCATION_URL, {t: type0, ref: ref.join(' '), i: i - 1, dt: dt}, function (data) {
      $(id).html(data);
      $(id + ' .colloc-result').mCustomScrollbar({
        theme: 'dark',
        scrollInertia: 0,
        mouseWheel: {preventDefault: true},
        autoHideScrollbar: true
      });
      $(id + ' .colloc-usage:eq(0)').click();
    });
  });

  // if ($('#Loading').is(':hidden')) {
  //     searchAndFillSentences({t: $(this).attr('data'), ref: $(this).attr('ref'), dt: 0});
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
    $("#Loading2").show();
    setTimeout(function() {
      $("#Loading2").hide();
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

  $('#FeedbackForm').submit(function (e) {
    e.preventDefault();
    var textarea = $(this).find('[name="comment"]');
    var msg = textarea.val().trim();
    if (msg) {
      $.post($(this).attr('action'), $(this).serialize(), function (r) {
        toastr.remove();
        toastr.success('反馈成功');
        textarea.val('');
        $('#FeedbackModal').modal('hide');
      });
    } else {
      toastr.remove();
      toastr.warning('请输入反馈内容');
    }
    textarea.focus();
  });

  $(".back-to-top").click(function() {
    $("html,body").animate({scrollTop: 0}, "fast");
    return false;
  });

  // $("#SidebarAffix").affix({
  //   offset: {
  //     top: 20,
  //     bottom: function () {
  //       return $(".footer").outerHeight(true) + $("#BackToTopAffix").outerHeight(true) + 40;
  //     }
  //   }
  // });

  $("#BackToTopAffix").affix({
    offset: {
      top: 0,
      bottom: function () {
        // TODO: fix position bugs on change of window length
        return $(".footer").outerHeight(true) + 20;
      }
    }
  });

  $("#Feedback").affix({
    offset: {
      top: 0,
      bottom: function () {
        // TODO: fix position bugs on change of window length
        return $(".footer").outerHeight(true) + 100;
      }
    }
  });

  $.clickStar = function(e) {
    e.preventDefault();
    $(e.target).toggleClass("glyphicon-star-empty");
    $(e.target).toggleClass("glyphicon-star");
  };

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
  $('#first').click();
});
