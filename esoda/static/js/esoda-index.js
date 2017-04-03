/*
* Logic for esoda index page.
*/

$(function () {
	'use strict';

  $("#AddBookmark").click(function(e){
    e.preventDefault();
    var bookmarkUrl = window.location.href;
    var bookmarkTitle = document.title;

    if ("addToHomescreen" in window && addToHomescreen.isCompatible) { // Mobile browsers
      addToHomescreen({ autostart: false, startDelay: 0 }).show(true);
    } else if (window.sidebar && window.sidebar.addPanel) { // Firefox <=22
      window.sidebar.addPanel(document.title, window.location.href,'');
    } else if ((window.sidebar && /Firefox/i.test(navigator.userAgent))
               || (window.opera && window.print)) { // Firefox 23+ and Opera <=14 
      $(this).attr({
        href: bookmarkUrl,
        title: bookmarkTitle,
        rel: "sidebar"
      }).off(e);
      return true;
    } else if( window.external && ("AddFavorite" in window.external)) { // For IE Favorite
      window.external.AddFavorite( bookmarkUrl, bookmarkTitle);
    } else { // for other browsers which does not support (Chrome/Safari/Opera15+)
      alert("您的浏览器不支持该操作。\n请按 " +
            (navigator.userAgent.toLowerCase().indexOf('mac') != -1 ? 'Command/Cmd' : 'CTRL') +
            "+D 添加收藏。");
    }
    return false;
  });

	
  $("#FeedbackTab a").click(function (e) {
    e.preventDefault();
    $(this).tab("show");
  });

});