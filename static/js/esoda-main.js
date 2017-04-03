/*!
 * Main logic for ESODA front end
 */

$(function () {
  'use strict';

  var getData = $.getData;

  // TODO: Initialize autocomplete etc.
  Storage.prototype.setObj = function(key, obj) {
    return this.setItem(key, JSON.stringify(obj))
  }
  Storage.prototype.getObj = function(key) {
    return JSON.parse(this.getItem(key))
  }
  function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  } 
  function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

  function insertHistory(history, val) {
    if (history.length > 0) {
      history = history.filter(function(item) {
        return item !== val;
      });
    }
    history.unshift(val);
    if (history.length > 5) history.pop();
    return history;
  }

  window.clearHistory = function() {
    if (("localStorage" in window) && window.localStorage !== null) {
      localStorage.setObj("history", []);
    } else {
      setCookie("history", "[]", 365);
    }
  }

  function storeHistory() {
    if ($("#SearchBox").val().length == 0) return;
    if (("localStorage" in window) && window.localStorage !== null) {
      var history = localStorage.getObj("history");
      history = insertHistory(history, $("#SearchBox").val());
      localStorage.setObj("history", history);
    } else {
      var history = JSON.parse(getCookie("history"));
      history = insertHistory(history, $("#SearchBox").val());
      setCookie("history", JSON.stringify(history), 365);
    }
  }

  function readHistory() {
    if (("localStorage" in window) && window.localStorage !== null) {
      var history = localStorage.getObj("history");
      if (history == null) {
        history = [];
        localStorage.setObj("history", history);
      }
    } else {
      var history = JSON.parse(getCookie("history"));
      if (history == "") {
        history = [];
        setCookie("history", JSON.stringify(history), 365);
      }
    }

    defaultList = $.map(history, function( value ) {
      return {label: value, desc: "", category: "最近搜过"};
    });
  }


  var defaultList = [];
  //clearHistory();
  readHistory();
  defaultList = defaultList.concat(getData(""));
  /*
  var defaultList = [];
  $.getJSON( "search.php", "", function(data, status, xhr) {
    defaultList = data;
  });
  */

  $.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
      var that = this,
        currentCategory = "";
      $.each( items, function( index, item ) {
        var li;
        if ( item.category != currentCategory ) {
          ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
          currentCategory = item.category;
        }
        li = that._renderItemData( ul, item );
        if ( item.category ) {
          li.attr( "aria-label", item.category + " : " + item.label );
        }
      });
      ul.append("<li class='ui-autocomplete-category ui-autocomplete-warnings'>" +
                  "<div class=\"inline\">按“回车”发起检索</div>" +
                  "<div class=\"right-float\">" +
                  "<a href=\"\" id=\"ClearHistory\" onclick=\"window.clearHistory()\">清除搜索历史" +
                  "<span class=\"glyphicon glyphicon-time\"></span></a></div></li>");
    },
    _renderItem: function( ul, item ) {
      return $( "<li>" )
        .append( "<div><span class=\"ui-autocomplete-label\">" + item.label + "</span>" +
                 "&nbsp;&nbsp;<span class=\"ui-autocomplete-desc\">" + item.desc + "</span></div>" )
        .appendTo( ul );
    }
  });
  
  function split( val ) {
    return val.split( /\s+/ );
  }
  function extractLast( term ) {
    return split( term ).pop();
  }
  function extractPrefix( term ) {
  	return term.replace("<strong>", "").replace("</strong>", "");
  }
  

  var cache = {};
  $( "#SearchBox" ).catcomplete({
    minLength: 0,
    source: function( request, response ) {

      var term = extractLast( request.term );
      if ( term.length < 1) {
        response( defaultList );
        return;
      }


      if (term in cache) {
        response( cache[ term ] );
        return;
      }

      var data = getData( {term: term} );
      var show = [];
      var matcher = new RegExp( "^" + term, "i" );
      // As experimented, the items in *data* are references through getData method,
      // so that there's a new array needed for showing.
      data.forEach(function (item) {
      	show.push(
      	{
      		label: item.label.replace(matcher, "<strong>" + item.label.match(matcher) + "</strong>"),
      		desc: item.desc,
      		category: item.category
      	});
      });
      console.log(show);
      cache[ term ] = show;
      response( show );
      /*
      $.getJSON( "search.php", request.term, function(data, status, xhr) {
        cache[ term ] = data;
        response( data );
      });
      */

  	},
    search: function() {
      if (this.value.length == 0) return true;
      var term = extractLast( this.value );
      if ( term.length < 1 ) {
        return false;
      }
    },
    focus: function( event, ui ) {
      return false;
    },
    select: function( event, ui ) {
      var terms = split( this.value );
      terms.pop();
      terms.push( extractPrefix(ui.item.value) );
      this.value = terms.join( " " );
      if (event.keyCode !== $.ui.keyCode.TAB)
        $( "#SearchForm" ).submit();
      else
        this.value += " ";
      return false;

      /*
      this.value = ui.item.value;
      $( "#SearchForm" ).submit();
      return false;
      */
    }
  })
  .focus(function() {
    if (this.value == "")
      $(this).catcomplete("search", "");
  });

  $("#SearchForm").on("submit", storeHistory);

  $.clickHeart = function(e) {
		e.preventDefault();
		$(e.target).toggleClass("glyphicon-heart-empty");
		$(e.target).toggleClass("glyphicon-heart");
  }

  $("#OpenRegister").click(function() {
    $("#ModalLogin").modal("hide");
    setTimeout(function() {
      $(document.body).addClass("modal-open");
    }, 500);
  })
});
