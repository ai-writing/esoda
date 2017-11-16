/*
* Logic for esoda index page.
*/

$(function () {
    'use strict';
  $("#FeedbackTab a").click(function (e) {
    e.preventDefault();
    $(this).tab("show");
  });

  $( "#SearchBox" ).val("");

  var curDisplay = 0;
  $(".pager li .glyphicon-chevron-right").click(function (e) {
    e.preventDefault();
    $('#UserFeedback div:eq(' + curDisplay + ')').hide();
    $('#UserFeedback div:eq(' + (curDisplay + 1) + ')').hide();
    curDisplay += 2;
    if (curDisplay >= $('#UserFeedback').children('div').length) curDisplay = 0;
    $("#UserFeedback div:eq(" + curDisplay + ')').show();
    $("#UserFeedback div:eq(" + (curDisplay + 1) + ')').show();
  });

  $(".pager li .glyphicon-chevron-left").click(function(e){
    e.preventDefault();
    $('#UserFeedback div:eq(' + curDisplay + ')').hide();
    $('#UserFeedback div:eq(' + (curDisplay + 1) + ')').hide();
    curDisplay -= 2;
    if (curDisplay < 0) curDisplay = $('#UserFeedback').children('div').length - 2;
    $("#UserFeedback div:eq(" + curDisplay + ")").show();
    $("#UserFeedback div:eq(" + (curDisplay + 1) + ")").show();
  });

    $('#btn-read').click(function() {
        console.log('test');
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
            (function addChar() {
                if (q) {
                    $('#SearchBox').val($('#SearchBox').val() + q[0]);
                    // console.log(q[0]);
                    q = q.slice(1);
                    setTimeout(addChar, 80);
                }
                $( "#SearchForm" ).submit();
            })();
        });
    }

    $('.example-btn-link').click(function() {
        if ($(this).text() == '同义表达') {
            fillWithExample('efficient');
        }
        if ($(this).text() == '不同搭配') {
            fillWithExample('wait');
        }
        if ($(this).text() == '中英混搜') {
            fillWithExample('减少 the demand of');
        }
        if ($(this).text() == '短语查找') {
            fillWithExample('make effort');
        }
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
