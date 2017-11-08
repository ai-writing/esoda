$(function(){       
  $("[href*='#']").click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var $target = $(this.hash);
      $target = $target.length && $target || $('[name="' + this.hash.slice(1) + '"]');
      if ($target.length) {
        var targetOffset = $target.offset().top;
        $('html,body').animate({
          scrollTop: targetOffset
        },
        1000);
        return false;
      }
    }
  });
  $("#guide0_index").hover(function(){ 
    $("#circle0").css({
      'background-color':'#63B7E6'
    }); 
  },function(){  
    $("#circle0").css({
      'background-color':'#d8d8d8'
    }); 
  });
  $("#guide1_index").hover(function(){ 
    $("#circle1").css({
      'background-color':'#63B7E6'
    }); 
  },function(){  
    $("#circle1").css({
      'background-color':'#d8d8d8'
    }); 
  });
  $("#guide2_index").hover(function(){ 
    $("#circle2").css({
      'background-color':'#63B7E6'
    }); 
  },function(){  
    $("#circle2").css({
      'background-color':'#d8d8d8'
    }); 
  });
  $("#guide3_index").hover(function(){ 
    $("#circle3").css({
      'background-color':'#63B7E6'
    }); 
  },function(){  
    $("#circle3").css({
      'background-color':'#d8d8d8'
    }); 
  });
});
