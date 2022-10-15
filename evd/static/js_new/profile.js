$(document).ready( function(){

    $("#refer").autocomplete({
        source: "/ajax/refer/",
        minLength: 4,
        select: function(event, ui) {
            $("#refer_id").val(ui.item.id)
        }
    });
    
    function selectOnBlur () {
    
     this.$input.parent().popover("hide");
    }
    
    $('.selects-up').selectize({
            allowEmptyOption: true,
            sortField: {field: 'text'},
            onChange: selectOnBlur
    });
    
    
    
    
    //$('#profile_sub').click(function(){
    //debugger;
    //form validation
    $(function () {
      if ($('#basic_profile_form').length > 0 ){
        $('#basic_profile_form').parsley().on('field:validated', function() {
            var ok = $('.parsley-error').length === 0;
            $('.bs-callout-info').toggleClass('hidden', !ok);
            $('.bs-callout-warning').toggleClass('hidden', ok);
        })
        .on('form:submit', function() {
            var form_data = $('#basic_profile_form').serializeArray();
    
            var orientation_status = $(this).attr("data-orientation_status");
            $(this).attr('data-save_role','True');
    
            // Appending Hidden Input Checked Values
            $.each($('#basic_profile_form').find('input[name=roles]:checked:hidden'),function(){
                form_data.push({"name": "roles", "value": $(this).val()});
            });
    
            var resp = evd.ajax_form_sub('/save_base_profile/',form_data, basic_resp_callback );
            return false; // Don't submit form for this demo
        });
      }
    });
    //});
    
    var orientation_complete = function(){
        ajax_sub('/save_base_profile/',{'step':'base_profile'},basic_resp_callback);
    }
    
    var basic_resp_callback = function(resp){
        var msg = 'Some error occurred.. Please try again.', cls_name = 'alert-danger';
        var save_role = $("#save_roles").attr('data-save_role');
        if(resp == 'Success'){
            msg = 'Your profile has been saved Successfully!..';
            cls_name = 'alert-success';
    
            if(save_role === 'True'){
                setTimeout(function(){
                    window.location.href = "/onboarding/";
                },1500);
            }else{
                if($("#orientation_status").text().trim()==="Incomplete"){
                    $('.nav-tabs a[href="#orientation"]').trigger('click');
                    //setTimeout(function(){
                      //  window.location.href = "/profile/#orientation/";
                        //window.location.reload();
                    //},1500);
                } else{
                    window.location.href = "/onboarding/";
                }
                //window.location.reload();
            }
        }
        $('#after_submit').removeClass('hidden alert-danger alert-success alert-info').addClass( cls_name ).find('.msg').text(msg);
    }
    
    
    $('#save_roles').click(function(){
        var orientation_status = $(this).attr("data-orientation_status");
        if(orientation_status === "True"){
            var form_data = {'step':'role_select'};
            $(this).attr('data-save_role','True');
            form_data['csrfmiddlewaretoken'] = $('#role_form').find('input[name=csrfmiddlewaretoken]').val();
            form_data['role_list']  = [];
            $.each($('#role_form').find('input[name=roles]:checked'),function(){
                form_data['role_list'].push($(this).val());
            });
            evd.ajax_sub('/save_base_profile/',form_data, basic_resp_callback );
        }else{
           $(".complete_orientation_alert").removeClass("hide");
           $(document).scrollTop(0);
        }
    });
    
    
    
    
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    
    
    Date.daysBetween = function( date1, date2 ) {
      //Get 1 day in milliseconds
      var one_day=1000*60*60*24;
    
      // Convert both dates to milliseconds
      var date1_ms = date1.getTime();
      var date2_ms = date2.getTime();
    
      // Calculate the difference in milliseconds
      var difference_ms = date2_ms - date1_ms;
      // Convert back to days and return
      return Math.round(difference_ms/one_day);
    }
    
    
    evd.save_dev_training = function(){
        var form_data ={};
        form_data['onboard_id'] = $('#Content_Volunteer_Training').data('onboarding_id');
        form_data['step_name'] = $('#Content_Volunteer_Training').data('step_name');
        evd.ajax_sub('/save_step/',form_data,save_admin_training_resp);
    }
    
    var save_dev_training_resp = function(){
    };
    evd.save_admin_training = function(){
        var form_data ={};
        form_data['onboard_id'] = $('#Content_Admin_Training').data('onboard_id');
        form_data['step_name'] = $('#Content_Admin_Training').data('step_name');
        evd.ajax_sub('/save_step/',form_data,save_admin_training_resp);
    }
    
    var save_admin_training_resp = function(){
    };
    //wellwisher training save
    evd.save_wellwisher_training = function(){
        var form_data ={};
        form_data['onboard_id'] = $('#Training').data('onboard_id');
        form_data['step_name'] = $('#Training').data('step_name');
        evd.ajax_sub('/save_step/',form_data,save_admin_training_resp);
    }
    
    var save_wellwisher_training_resp = function(){
    };
    
    $('#sedob,.date_picker').datepicker({
            dateFormat: "yy-mm-dd",
    });
    
    
    evd.se_submit = function(){
        var $seform = $('#Self_Evaluation').find('form');
        var form_elements = $seform.find('.form-check-input[name!=""],.form-control[name!=""]');
        var form_unique_ele=[], check_inputs=[], non_check_inputs=[];
        var form_data = [], post_data={};
        $.each(form_elements,function(){
                if(!~$.inArray(this.name,form_unique_ele)) form_unique_ele.push(this.name);
        });
        $.each(form_unique_ele, function(){
                var ele = $('[name='+this+']');
                var qtn = $('.'+this).text();
                var temp = {};
                if(ele.hasClass('form-check-input')){
                    var checked_ele = $(ele).filter(':checked');
                    if(checked_ele.length>1){
                        $.each(checked_ele,function(i){
                            if(i==0){
                                temp[qtn] = $(this).parent().text().trim();
                            }else{
                                temp[qtn] += ';'+$(this).parent().text().trim();
                            }
                        });
                    }else{
                         temp[qtn] = $(ele).filter(':checked').parent().text().trim();
                    }
                 }else{
                         temp[qtn] = $(ele).val().trim();
                 }
                form_data.push(temp);
        });
        console.log(form_data);
        post_data['form_dump'] = JSON.stringify(form_data);
        post_data['role'] = 'teacher';
        post_data['onboard_id'] = $seform.data('onboarding_id')
        console.log(post_data);
        evd.ajax_sub('/selfeval_response/',post_data,se_form_resp);
        return false;
    }
    
    var se_form_resp = function(){
    };
    var av_form_resp = function(){
    };
    
    /*<<<<<<< HEAD
    evd.preferences_submit = function(source){
        var source = source || "onboard";
    =======*/
    evd.preferences_submit = function(source, id){
        var source = source || "onboard";
        var user_id= id || "";
    /*>>>>>>> evd_dev*/
        var av_form = $('#availability_form');
        var availability = $('input[name="availability"]:checked').val();
        var form_data = {};
        form_data['availability'] = availability;
        form_data['source'] = source;
    /*<<<<<<< HEAD
    =======*/
        form_data['user_id'] = user_id;
    /*>>>>>>> evd_dev*/
        if(availability === "available"){
            form_data['from_date'] = av_form.find('#from').val();
            form_data['to_date'] = av_form.find('#to').val();
            form_data['pref_slots']=av_form.find('#slots').val();
            form_data['pref_days']=av_form.find('#days').val();
            console.log( form_data['pref_slots'])
            var pref_sub = [];
            $("input[name='pref_sub']:checked").each(function(){
                pref_sub.push($(this).val());
            });
            pref_sub = pref_sub.join(";")
            form_data['pref_sub'] = pref_sub;
            av_form.find('.timing-inner-wrapper.controls').each(function(index){
                    var pref_days = $(this).find('.prefered_days').val();
                    var start_time = $(this).find('select[name=prefered_timings_mor]').val();
                    var end_time = $(this).find('select[name=prefered_timings_eve]').val();
                    if(index == 0){
                        form_data['pref_days'] = pref_days;
                        form_data['pref_times'] =  start_time+'-'+end_time;
                    }else{
                        form_data['pref_days'] += ';'+pref_days;
                        form_data['pref_times'] +=  ';'+start_time+'-'+end_time;
                    }
            });
        }
        else{
            form_data['reason'] = $("select[name='reason']").val();
            if(!$(".follow_up").hasClass('hidden')){
                form_data['follow_up_date'] = av_form.find('#follow_up').val();
            }
        }
        form_data['onboard_id'] = av_form.data('onboarding_id');
        evd.ajax_sub('/save_availability/',form_data,av_form_resp);
    };
    
    /* Generic Post function */
    
    evd.ajax_form_sub = function(url,serial_form_data,callback){
            var data_obj = {};
            $.each(serial_form_data,function(){
                if(!data_obj.hasOwnProperty(this.name)){
                    data_obj[this.name] = this.value;
                }else{
                    data_obj[this.name] += ';'+this.value;
                }
            });
           $.post(url,data_obj,function(resp){
                callback(resp);
            });
    };
    
    evd.ajax_sub = function(url,post_data,callback){
            var csrftoken = getCookie('csrftoken');
            post_data['csrfmiddlewaretoken'] = csrftoken;
            $.post(url,post_data,function(resp){
                callback(resp);
            });
    
    };
    
    
    });
    