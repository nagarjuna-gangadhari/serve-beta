$(document).ready(function(){
  $("body").on("click",".orientation_close", function(){
            var url = $("#orientation_modal #player").attr("src");
            url = url.replace("&autoplay=1", "");
            $('#orientation_modal #player').prop('src','');
            $("#orientation_modal #player").attr("src", url);
  });

});

function play_video() {
  $("#orientation_modal #player")[0].src += "&autoplay=1";
  var form_data ={};
  form_data['onboard_id'] = '';
  form_data['step_name'] = 'Orientation';
  evd.ajax_sub('/save_step/',form_data,'');
  $('.onboarding_status #orient_complete').removeClass('hide');
  $('.onboarding_status #orient_complete').addClass('show');
}
