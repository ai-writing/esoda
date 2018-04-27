/*
* Logic for esoda index page.
*/

$(function () {
    'use strict';
  $("#FeedbackTab a").click(function (e) {
    e.preventDefault();
    $(this).tab("show");
  });

  // $( "#SearchBox" ).val("");

  var curDisplay = 0;
  var numDisplay = 3;
  var feedbackElements = $('#UserFeedback > div');
  for (var i = 0; i < numDisplay; i++) {
    $("#UserFeedback > div:eq(" + (curDisplay + i) + ')').show();
  }
  $(".pager li .glyphicon-chevron-right").click(function (e) {
    e.preventDefault();
    feedbackElements.hide();
    curDisplay += numDisplay;
    if (curDisplay >= feedbackElements.length) curDisplay = 0;
    for (var i = 0; i < numDisplay; i++) {
        $("#UserFeedback > div:eq(" + (curDisplay + i) + ')').show();
    }
  });

  $(".pager li .glyphicon-chevron-left").click(function(e){
    e.preventDefault();
    $('#UserFeedback div').hide();
    curDisplay -= numDisplay;
    if (curDisplay < 0) curDisplay = feedbackElements.length - 1 - (feedbackElements.length - 1) % numDisplay;
    for (var i = 0; i < numDisplay; i++) {
        $("#UserFeedback > div:eq(" + (curDisplay + i) + ')').show();
    }
  });
/*
    $('#btn-read').click(function() {
        $('#feedback').show();
        $('#btn-read').hide();
        $('#btn-unread').show();
      });

    $('#btn-unread').click(function() {
        $('#feedback').hide();
        $('#btn-unread').hide();
        $('#btn-read').show();
      });

  $('#MsgForm').submit(function (e) {
    e.preventDefault();
    var textarea = $(this).find('[name="message"]');
    var msg = textarea.val().trim();
    if (msg) {
      $.post($(this).attr('action'), $(this).serialize(), function (r) {
        toastr.remove();
        toastr.success('留言成功');
        textarea.val('');
      });
    } else {
      toastr.remove();
      toastr.warning('请输入留言内容');
    }
    textarea.focus();
  });
*/
  // $('#SearchBox').click(function (e) {
  //   $('.jumbotron').css("padding-top","64px");
  //   $('#SearchBox').catcomplete('search'); 
  // });

    var ANIMATION_ON = false;

    function scrollToTop(duration, callback) {
        var x = 0, initialY = scrollY, ease = function(n) {
            return n * (2 - n);
        };
        var interval = setInterval(function () {
            x += 20 / duration;
            scrollTo(scrollX, x > 1 ? 0 : (1 - ease(x)) * initialY);
            if (x > 1) {
                clearInterval(interval);
                callback && callback();
            }
        }, 20);
    }

    function fillWithExample(text) {
        // scroll to top
        // clear and fill in text
        // (wait drop down and select suggestion)
        // click search button
        if (ANIMATION_ON || !text) {
            return;
        }
        ANIMATION_ON = true;
        var q = text.trim();
        // $('html,body').animate({ scrollTop: 0 }, 'fast', 'swing', function() {
        // for campatibility with Chrome:
        scrollToTop(300, function () {
            $('#SearchBox').val('');
            $('#SearchBox').focus();
            (function addChar() {
                if (q) {
                    $('#SearchBox').val($('#SearchBox').val() + q[0]);
                    q = q.slice(1);
                    setTimeout(addChar, 80);
                } else {
                    window.location.href="/?q="+text+"&";
                }
                // $( "#SearchForm" ).submit();
            })();
        });
    }

    $('.example-btn-link').click(function() {
        fillWithExample($(this).attr('value'));
        // window.location.href="/?q="+$(this).attr('value')+"&";
    });

    // Fix Safari cache on back
    if (navigator.userAgent.indexOf("Safari") >= 0) {
        $(window).bind("pageshow", function (event) {
            if (event.originalEvent.persisted) {
                $("#SearchInput").attr('autocomplete', 'off');
                $("#NavSearchInput").attr('NavSearchInput', 'off');
            }
        });
    }
});
