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
});
