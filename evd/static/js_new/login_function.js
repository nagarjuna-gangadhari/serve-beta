$(document).ready(function(){
    var $login_signup_form = $("#login-signup-form"),
        $modal = $("#login-modal");
    $("#signup-trigger").click(function(e){
        var is_authenticated = "{{ user.is_authenticated }}";
        
        if(is_authenticated == "True"){
            window.location = "/myevidyaloka/";
            return;
        }
        e.preventDefault();
    });

    $("#login-trigger").click(function(e){
        var is_authenticated = "{{ user.is_authenticated }}";
        
        if(is_authenticated == "True"){
            window.location = "/myevidyaloka/";
            return;
        }
        e.stopPropagation();
        e.preventDefault();
    });

    $('#partner-signup').click(function(e){
        e.preventDefault();
        var data_serial = $('form#partner-signup-trigger').serializeArray();
        data_serial.push({'name' : 'partnertype', 'value' : $(this).parents("div").find('span').text()});
         $("#ajax_loader").show();
        $.ajax({
            url:"/partner/signup/",
            method:"POST",
            data : data_serial,
            success:function(resp) {
                if(resp.status) {
                    alert(resp.message);
                } else {
                    setTimeout(function(){
                        alert(resp)
                        if (resp == "Please enter email-id"){
                             $('#partner-modal').modal('show');
                        }else{
                              $('#partner-modal').modal('hide');
                              window.location = "/?show_popup=true";
                        }

                    },2000);
                    $('#partner-modal').modal('show');
                }
            },
            complete: function(){
                 $("#ajax_loader").hide();
              }
        });
    });

});
