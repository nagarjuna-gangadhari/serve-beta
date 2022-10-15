var show_message = function(message, donot_let_close, options){
  options = options || {};
  if(options.pre_show){
    options.pre_show();
  }
  var $main_content = $("#content-container");
  var $message = $(".message");
  var $overlay = $(".message-overlay").removeClass("hide");
  $message.removeClass("hide").addClass("in").children("p").html(message);
  if(!donot_let_close){
    $overlay.on("click", options, hide_message);
  }
}

var hide_message = function(){

  var $message = $(".message");
  var $main_content = $("#content-container");
  var $overlay = $(".message-overlay").addClass("hide");
  $main_content.removeClass("faded");
  $message.removeClass("in").addClass("hide").children("p").html("");
  $overlay.off("click", hide_message);
}
