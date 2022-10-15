$(document).ready(function(){
    if (performance.navigation.type !=2) {
        if (typeof(Storage) != undefined){
            sessionStorage.clear();
        } 
      } 
$('.demand_label').select2();
    window.pref_med= $(".med").attr("id");
    window.pref_subject= $("#pref_subject_id").val();
    window.usr_status= $(".usr").attr("id");
    window.course_id= $("#course_id").val();
    $("#demand_message_alert").addClass('hide');    
    if (sessionStorage.getItem("pref_medium") ){
        pref_med = JSON.parse(sessionStorage.getItem("pref_medium"));
    }   
   
    $(".demand_label option[data-value=" + pref_med + "]").attr('selected', true).trigger("change");
    window.pref_grade= $("#pref_grade_id").val();
    
    $(".demand_label").on('change',function(){
        if (typeof(Storage) != "undefined" ) {
            sessionStorage.setItem("pref_subject",  JSON.stringify($("#sub_opts").val() ));
            sessionStorage.setItem("pref_grades", JSON.stringify($("#grade_opts").val() )); 
        }    
    });

    $(function(){
     refresh_data();

    });
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var loading = function() {
            // add the overlay with loading image to the page
            var over = '<div id="overlay" style="z-index: 10;">' +
                '<img id="loading" src="/static/images/loader_demand.gif" >' +
                '</div>';
            $(over).appendTo('#thumbs_div');

    };

    var language_flag = 0;
    //get data from filters

    var get_filter_data = function(){
            var sel_days = [];
            var sel_langs = [];
            var sel_slots = [];
            var sel_cont = [];
            var filter_days = $('#filter_days').find('.optns').find('.demand_label > option:selected');
            _.forEach(filter_days,function(u){
               sel_days.push($(u).data('value'));
            });
            if (sel_days.length > 0) {
                sessionStorage.setItem("pref_day", JSON.stringify(sel_days));
            }
            
            var sel_slots = $('#sel_timerange').val();
            if (sessionStorage.getItem("pref_time")){
                sel_slots = sessionStorage.getItem("pref_time") 
            }
            var filter_langs = $('#filter_langs').find('.optns').find('.demand_label > option:selected');
            _.forEach(filter_langs,function(u){
               language_flag = 0;
               if(pref_med != $(u).data('value')){
                    language_flag = 1;
               }
               sel_langs.push($(u).data('value'));
               if(sel_langs.includes(pref_med)==true){
                   language_flag = 0;
               }
            });
            if (sel_langs==null || sel_langs=='' || sel_langs=='undefined'){
                $("#auth_lang_id").removeClass('hidden');
            }else{
                $("#auth_lang_id").addClass('hidden');
            }
            var filter_cont = $('#filter_cont').find('.optns').find('.demand_label > option:selected');
            _.forEach(filter_cont,function(u){
               sel_cont.push($(u).data('value'));
            });
            if (sel_cont.length == 1){
                if (sel_cont.includes('S')==true){
                    $("#demand_alert_for_s_type").show();
                    window.setTimeout(function () {
                        $("#demand_alert_for_s_type").fadeTo(3000, 0).slideUp(300, function () {
                            $(this).remove();
                        });
                    }, 5000);
                    $("#demand_alert_for_c_type").hide();
                }else if (sel_cont.includes('C')==true){
                    $("#demand_alert_for_c_type").show();
                    window.setTimeout(function () {
                        $("#demand_alert_for_c_type").fadeTo(3000, 0).slideUp(300, function () {
                            $(this).remove();
                        });
                    }, 5000);
                    $("#demand_alert_for_s_type").hide();
                }
            }else{
                $("#demand_alert_for_s_type").hide();
                $("#demand_alert_for_c_type").hide();
            }
            if((language_flag == 1) && (usr_status=="true")){
                $("#demand_alert_for_s_type").hide();
                $("#demand_alert_for_c_type").hide();
                $("#medium_alert").removeClass("hidden");
                window.setTimeout(function () {
                    $("#medium_alert").fadeTo(3000, 0).slideUp(300, function () {
                        $(this).alert('close');
                    });
                }, 5000);
                language_flag = 0;
                //alert("Your preferred language is not matching your filter");
            }
            else if((language_flag != 1) && (usr_status=="true")){
                /*$("#demand_alert_for_s_type").show();*/
                $("#medium_alert").addClass("hidden");
            }
            return [sel_days,sel_slots,sel_langs,sel_cont]
    };
    
    $(".demand2_label").change(function(){
        refresh_data();
    });
    $('#pref_medium').on("change",function() {
        window.pref_subject = ''
        window.pref_grade = ''
        $("#sub_opts option:selected").removeAttr("selected").trigger("change"); 
        $("#grade_opts option:selected").removeAttr("selected").trigger("change");
    });
    $('#preferredDayId').on("change",function() {
        window.pref_subject = ''
        window.pref_grade = ''
        $("#sub_opts option:selected").removeAttr("selected").trigger("change"); 
        $("#grade_opts option:selected").removeAttr("selected").trigger("change");
    });
    // Month filter relative to subject filter
    $('#filters_div').on('click','button.filter',function(event){
        //Getting subject filter data
        var months = ['January','February','March', "April","May","June","July","August","September","October","November","December"];
        var checked_opts = $('#sub_opts').find('.fil_opts:selected');
        var sub_fil_data = '';
        var un_checked = $('#sub_opts').find('.fil_opts').not(':selected');
        if(checked_opts.length!=0){
            _.each(checked_opts,function(u){
                sub_fil_data += '.'+$(u).data('value')+' ';
            });
        }
        var that= $(this);
        $(this).addClass('fil_active').siblings().not(that).removeClass('fil_active');
        var sel_class = that.data('filter');
        if(sel_class != ".All"){
            _.each(filter_years,function(year){
                _.each(months,function(uu){

                $('.'+uu+year).fadeOut(500);
              });
            });
            if(checked_opts.length!=0){
                _.each(checked_opts,function(u){
                    sub_fil_data = '.'+$(u).data('value')+' ';
                    $(sel_class + sub_fil_data).fadeIn(500);
                });
            }else{
                $(sel_class).fadeIn(500);
            }
            $('.thumbnail').attr('style','');
        }else{
            if (checked_opts.length!=0){
                _.each(checked_opts,function(u){
                    $('.'+ $(u).data('value')).fadeIn(500);
                });
            }
            if (un_checked.length!=0){
                _.each(un_checked,function(u){
                    $('.'+ $(u).data('value')).fadeOut(500);
                });
            }
            _.each(filter_years,function(year){
            _.each(months,function(uu){
                if (checked_opts.length!=0){
                    _.each(checked_opts,function(u){
                        $('.'+ $(u).data('value')+ '.'+uu+year).fadeIn(500);
                    });
                }else{
                    $('.'+uu+year).fadeIn(500);
                }
            });
            });
        }
    });

    // Subject filter on click
    $("#sub_opts").on('change',function(){
        subjectFilter();
    });
    $("#grade_opts").on('change',function(){
        gradeFilter();
    });
    
    var refresh_data  =  function()
        {
                fil_data = get_filter_data();
                loading();
               
                
                if (typeof(Storage) != "undefined" ) {
                    //sessionStorage.setItem("pref_day", JSON.stringify(fil_data[0])  );
                    sessionStorage.setItem("pref_medium", JSON.stringify(fil_data[2]));
                } 
                days_list = [];
                $("#preferredDayId .demand_label option:selected").each(function() {
                    days_list.push($(this).attr('name'));
                });
                if( days_list.length==0 && sessionStorage.getItem('pref_day') !=null || sessionStorage.getItem('pref_day') !='') {
                    days_list = JSON.parse(sessionStorage.getItem('pref_day'))
                }
                lang = [];
                $("#pref_medium .demand_label option:selected").each(function() {
                    lang.push($(this).attr('name'));
                });
                var csrftoken = getCookie('csrftoken');
                if( (fil_data[0]).length < 2 ){
                    $('#demand_alert_for_s_type').removeClass('hide');
                    $('#demand_alert_for_c_type').addClass('hide');
                }else{
                    $('#demand_alert_for_s_type').addClass('hide');
                    $('#demand_alert_for_c_type').removeClass('hide');
                }
                var cnt=[];
                _.forEach(fil_data[3],function(u){
                    cnt.push($(u).data('value'));
                 });
                $('#filter_days,#filter_times').tooltip('hide');
                input_short_url = $("#input_short_url").val()
                var sel_day = JSON.stringify(fil_data[0])
                if (sessionStorage.getItem("pref_day") != "" && sessionStorage.getItem("pref_day") != null){
                    
                    sel_day  = JSON.parse(sessionStorage.getItem("pref_day"))

                }
                
                $.post('/v2/get_demand/',{'csrfmiddlewaretoken':csrftoken,'sel_days':sel_day,'sel_cont':JSON.stringify(cnt),'sel_langs':JSON.stringify(fil_data[2]),'sel_slots':JSON.stringify(fil_data[1]),'sel_nature':JSON.stringify(fil_data[3]),'subject':course_id,"input_short_url":input_short_url},function(resp){
                    resp9=resp;
                    var demand_list_data = '';
                    //var colors = ['rgba(9, 87, 165, 0.8)', 'rgba(30, 148, 82, 0.9)',  'rgba(218,93,44,0.9)'];
                    var colors = ['rgba(254, 254, 254, 0.8)', 'rgba(254, 254, 254, 0.9)',  'rgba(254, 254, 254, 0.9)'];
                    var j = 0;
                    var subject_name = [];
                    if (resp!=null && resp!='' && resp!='undefined'){
                        if (resp.data!=null && resp.data!='' && resp.data!='undefined'){
                            var jsonObjs = resp.data;
                            for ( i = 0; i < jsonObjs.length; i++) {
                                //console.log("****** CENTERES : " + jsonObjs[i]['center_names'])
                                var subject= jsonObjs[i]['subject'];
                                subject_name = subject.split('_')
                                var grade = jsonObjs[i]['grades'];
                                demand_list_data += '<div class="div_width_mob col-md-3 col-xs-6 mix '+jsonObjs[i]['subject']+' ';
                                var my_grades = jsonObjs[i]['grades'].toString();
                                if (my_grades.indexOf('5')>-1){demand_list_data += '5 ';}
                                if (my_grades.indexOf('6')>-1){demand_list_data += '6 ';}
                                if (my_grades.indexOf('7')>-1){demand_list_data += '7 ';}
                                if (my_grades.indexOf('8')>-1){demand_list_data += '8 ';}
                                if (my_grades.indexOf('9')>-1){demand_list_data += '9 ';}
                                if (my_grades.indexOf('10')>-1){demand_list_data += '10 ';}
                                if (my_grades.indexOf('11')>-1){demand_list_data += '11 ';}
                                if (my_grades.indexOf('12')>-1){demand_list_data += '12 ';}
                                var months_data = (jsonObjs[i]['tags']['months']).toString();
                                if (months_data.indexOf(',')>-1){
                                    var months_array  = months_data.split(',');
                                    _.each(months_array,function(u){
                                        demand_list_data += ''+u+' ';
                                    });
                                }else{
                                    demand_list_data += jsonObjs[i]['tags']['months'];
                                }
                                demand_list_data += ' ">';
                                if(window.usr_status=='true'){
                                    var inpt_time = ''
                                    if (sessionStorage.getItem("pref_time") ){
                                        inpt_time =  sessionStorage.getItem("pref_time");
                                    }
                                    else{
                                         inpt_time = $("#sel_timerange").val();
                                    }
                                    lang = $("#pref_medium").val();
                                    inpt_time1 = inpt_time.substring(6,11);
                                    inpt_time = inpt_time.substring(0,5);
                                    demand_list_data += '<a class="already" href="/v2/demandDetails/?inpt_time1='+inpt_time1+'&inpt_time='+inpt_time+'&course_id='+jsonObjs[i]['course_id']+'&lang='+lang+'&month='+jsonObjs[i]['tags']['months']+'&year='+jsonObjs[i]['tags']['years']+'&backfill='+jsonObjs[i]['backfill']+'&days_list='+days_list+'&provisional='+jsonObjs[i]['is_provisional']+'" style="cursor: pointer; text-decoration: none;">';
                                }
                                else{
                                    demand_list_data += '<a data-toggle="modal" data-target="#login-modal" id="login-trigger" class="already" style="cursor:pointer;text-decoration:none">';
                                }
                                //demand_list_data += '<div class="thumbnail" style="border-radius: 5px !important;padding: 0px ! important;"><div class=" caption row thumb_row" style="background-color: '+colors[j]+';height: 80px; border-radius: 3px !important;border-bottom: 2px solid #e6e6e6;text-align: center;margin:1px auto ! important;" >';
                                //demand_list_data += '<h6 class="fontSize20" align="center" style="font-size:20px;color:white;"><b>';
                                demand_list_data += '<div class="thumbnail" style="border-radius: 5px !important;padding: 0px ! important;"><div class=" caption row thumb_row" title="' + jsonObjs[i]['center_names'] + '" style="background-color: ' + colors[j]+';height: 48px; border-radius: 3px !important;border-bottom: 2px solid #e6e6e6;text-align: center;margin:1px auto ! important; padding: 0px !important;" >';
                                demand_list_data += '<h6 class="fontSize20" align="center" style="font-size:20px;color:#666666;"><b>';
                                for(k=0;k<subject_name.length;k++){
                                    demand_list_data += ''+subject_name[k]+' ';
                                }
                                demand_list_data += '</b></h6></div>';
                                //demand_list_data += '<div class="caption captionMob" style="background-color: white;height: 140px;">';
                                demand_list_data += '<div class="caption captionMob" style="background-color: white;height: 85px;">';
                                //demand_list_data +=	'<h6 style="color:'+colors[j]+';margin-top:10%;font-size: 18px;">Available For Grades: <br><br>';
                                demand_list_data +=	'<h6 style="color:#666666;margin-top:5.5%;font-size: 15px;margin-left:10px;">Available For Grades: <br><br>';
                                var grade_list = grade.toString().split(",");
                                if (grade_list.length>0){
                                        for(k=0;k<grade_list.length;k++){
                                            demand_list_data +=	' '+grade_list[k];//+'th';
                                            if (k!=grade_list.length-1){
                                                demand_list_data += ',';
                                            }
                                        }
                                    }
                                if (jsonObjs[i]["backfill"]==true){
                                    demand_list_data += '</div><div class="row thumb_row" data-toggle="tooltip" title="High Priority Requirement" style="height:40px ! important;background:yellow" ><div class="col-xs-12 col-sm-7 stat_left" style="padding:11px; font-size: 12px;color:black !important;">'+jsonObjs[i]['running_courses']+' teachers';
                                } else if (jsonObjs[i]["is_provisional"] == true){
                                    demand_list_data += '</div><div class="row thumb_row" data-toggle="tooltip" title="Projected Requirement" style="height:40px ! important;background:#c0f7c0" ><div class="col-xs-12 col-sm-7 stat_left" style="padding:11px; font-size: 12px;color:black !important;">'+jsonObjs[i]['running_courses']+' teachers';
                                } else {
                                    demand_list_data += '</div><div class="row thumb_row" title="Normal Priority Requirement" style="height:40px ! important;background:orange" " ><div class="col-xs-12 col-sm-7 stat_left" style="padding:11px; font-size: 12px;color:black !important;">'+jsonObjs[i]['running_courses']+' teachers';
                                }
                                demand_list_data += ' teaching</div><div class="col-xs-12 col-sm-5 stat border_radius" style="padding: 11px 2px 0px 0px;font-size: 12px;color:black">'+jsonObjs[i]['pending_courses']+' more needed</div></div></div></a></div>';
                                j++;
                                if(j>colors.length-1){
                                    j=0;
                                }
                            }
                        }
                    }
                    else{
                        demand_list_data = 'No Data Available.';
                    }
                    filter_subs = [];
                    filter_months = [];
                    filter_years = [];
                    _.forEach(resp9.data, function(u){
                        filter_months = (_.union(u.tags.months,filter_months));
                    });
                    _.forEach(resp9.data, function(v){
                        filter_years = (_.union(v.tags.years,filter_years));
                    });

                    var allMonths = ['January','February','March', "April","May","June","July","August","September","October","November","December"];
                    filter_months.sort(function(a,b){
                        return allMonths.indexOf(a) > allMonths.indexOf(b);
                    });
                    var allYears = ['09','10','11','12','13','14','15','16','17','18','19','20','21','22'];
                    filter_years.sort(function(a,b){
                        return allYears.indexOf(a) > allYears.indexOf(b);
                    });
    
                    var filter_template = _.template("<div class='col-xs-12 col-sm-12 col-md-12 col-lg-12' style='argin-top: -30px;'>"+
                                                    "<div class='row fil_rw' style='display: inline-flex;' >"+
                                                    "<% if (resp9.data != ''){ %>"+
                                                     "<h4 style='width: -moz-max-content;display: inline-table;'>Courses starting from:</h4>"+
                                                     "<% } %>"+
                                                     "<hr style='margin:5px !important'>"+
                                                    "<% if (resp9.data != '') %>" +
                                                    "<button class='filter  btn-link fil_active' style='font-size:12px;margin-right: -1%;' data-filter='.All' id='monthFilterId'>All</button>"+

                                                  "<% _.forEach(resp9.date,function(v){%>"+
                                                  "<button class='filter  btn-link ' style='font-size:12px;margin-right: -1%;' data-filter='.<%= v %>'><%=v%></button>"+
                                                  "<% }) %>"+
                                                    "</div>"+
                                                    "</div>");
                    var subj_filter = _.template( "<% _.forEach(resp9.unique_subjects,function(u){%>"+
                            "<div class='checkbox'>"+
                               " <label class='demand_label'>"+
                                    "<option type='checkbox' data-value='<%=u%>' class='fil_opts' style='margin-left: -15px;' <% if (u == window.pref_subject) {%> selected <%}%>><%=u%>"+"</option>"+
                                "</label>"+
                            "</div>"+
                            "<% }) %>");
                    var grade_filter = _.template("<% _.forEach(resp9.unique_grades,function(u){%>"+
                            "<div class='checkbox'>"+
                               " <label class='demand_label' >"+
                                    "<option type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_grade) {%> selected <%}%>><%=u%>"+"</option>"+
                               "</label>"+
                            "</div>"+
                            "<% }) %>");
    
                    /*demand_template(resp9.data);*/
                    subj_filter(resp9.unique_subjects);
                    grade_filter(resp9.unique_grades);
                    filter_template(resp9.unique_subjects);
                    if(resp9.unique_subjects.length == 0){
                        $('#filter_subjects').hide();
                    }else{
                        $('#filter_subjects').show();
                    }
                    if(resp9.unique_grades.length == 0){
                        $('#filter_grades').hide();
                    }else{
                        $('#filter_grades').show();
                    }
                    if(resp9.data.length == 0){
                        $('#thumbs_div').css('margin-top', '-23px');
                        $('.not_able2_find_opportunity').css('display','block');
                        $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Course Matching Your filters..!</p>');
                        $('#thumbs_div').html('<img class="imageCss" style="margin-left: 192px;" src="/static/img/opp_not_found.jpeg">');


                    }else{
                         $('.not_able2_find_opportunity').css('display','none');
                         $('#thumbs_div').css('margin-top', '10px');

                        $('#thumbs_div').html(demand_list_data);
                    }
                    $('#filters_div').html(filter_template);
                    $('#sub_opts').html(subj_filter);
                    $('#grade_opts').html(grade_filter);
                    subjectFilter();
        //            gradeFilter();
                    // window.sr = ScrollReveal();
                    // sr.reveal('.thumbnail');
                    if(pref_subject!=null && pref_subject!='' && pref_subject!='undefined'){
                        $("#sub_opts").trigger('click');
                    }
                    if (sessionStorage.getItem('pref_time')){
                        time_arr = (sessionStorage.getItem('pref_time')).split(";")
                        start_time = time_arr[0]
                        end_time = time_arr[1]

                        time_arr = start_time.split(":")
                        start_hour = time_arr[0]
                        start_minute = time_arr[1]

                        time_arr = end_time.split(":")
                        end_hour = time_arr[0]
                        end_minute = time_arr[1]
                        if ((start_hour && start_minute) || (end_hour && end_minute)){
                            $('#slider-range').trigger('slidechange');
                            setSliderValues(start_hour,start_minute, end_hour, end_minute)

                        }
                    }
                }).done(function(){
                    if (sessionStorage.getItem("pref_subject") || (sessionStorage.getItem('pref_grade')) ){
                        pref_subject1 = JSON.parse(sessionStorage.getItem("pref_subject"));
                        pref_grade1 = JSON.parse(sessionStorage.getItem("pref_grades"));
                        if (pref_subject1) {
                            for(var i = 0; i < pref_subject1.length; i++){
                                $("#sub_opts").val(pref_subject1).change();
                            }
                        }

                        if (pref_grade1) {
                            for(var i = 0; i <pref_grade1.length; i++){
                                $("#grade_opts").val(pref_grade1).change();
                            }
                        }
                    }
                });
        }
    
    
function setSliderValues(start_hour,start_minute, end_hour, end_minute){
    var start_hour = start_hour
    var start_minute = start_minute
    
    if (start_hour.length == 1) start_hour = '0' + start_hour;
    if (start_minute.length == 1) start_minute = '0' + start_minute;
    if (start_minute == 0) start_minute = '00';
    if (start_hour >= 12) {
        if (start_hour == 12) {
            start_hour = start_hour;
            start_minute = start_minute + " PM";
        } else {
            start_hour = start_hour - 12;
            start_minute = start_minute + " PM";
        }
    } else {
        start_hour = start_hour;
        start_minute = start_minute + " AM";
    }
    if (start_hour == 0) {
        start_hour = 12;
        start_minute = start_minute;
    }

    $('.slider-time').html(start_hour + ':' + start_minute);
    var end_hour = end_hour
    var end_minute = end_minute
    
    if (end_hour.length == 1) end_hour = '0' + end_hour;
    if (end_minute.length == 1) end_minute = '0' + end_minute;
    if (end_minute == 0) end_minute = '00';
    if (end_hour >= 12) {
        if (end_hour == 12) {
            end_hour = end_hour;
            end_minute = end_minute + " PM";
        } else if (end_hour == 24) {
            end_hour = 11;
            end_minute = "59 PM";
        } else {
            end_hour = end_hour - 12;
            end_minute = end_minute + " PM";
        }
    } else {
        end_hour = end_hour;
        end_minute = end_minute + " AM";
    }
    $('.slider-time2').html(end_hour + ':' + end_minute);
    
    var start_time = get_24hrtime(start_hour + ':' + start_minute);
    
    var end_time = get_24hrtime(end_hour + ':' + end_minute);
    $('#sel_timerange').val(start_time+';'+end_time);
    sessionStorage.setItem('pref_time',$('#sel_timerange').val());
    var starting_value = $("#slider-range").slider('option').values[0];
    var ending_value = $("#slider-range").slider('option').values[1];
   
        sessionStorage.setItem('starting_value',starting_value);
        sessionStorage.setItem('ending_value',ending_value);
  
    if (sessionStorage.getItem('starting_value')){
        $("#slider").slider('values',0,sessionStorage.getItem('starting_value'));
        $("#slider").slider('values',0,sessionStorage.getItem('ending_value'));
    }
    

    
    
}
    
    // Time picker JS
    $("#slider-range").slider({
        
        range: true,
        min: 420,
        max: 1260,
        step: 15,
        values: [420, 1260],
        change: function (e, ui) {
            var start_hour = Math.floor(ui.values[0] / 60);
            // console.log("bvcnsdb"+start_hour);
            var start_minute =  start_minute = ui.values[0] - (start_hour * 60);
            var end_hour = Math.floor(ui.values[1] / 60);
            var end_minute = ui.values[1] - (end_hour * 60);
            setSliderValues(start_hour, start_minute, end_hour, end_minute, store_val=1) 
            refresh_data();
        }
    
    });
    
    // Convert to 24 hr format
    var get_24hrtime =  function(time){
    
        var hours = Number(time.match(/^(\d+)/)[1]);
        var minutes = Number(time.match(/:(\d+)/)[1]);
        var AMPM = time.match(/\s(.*)$/)[1];
        if(AMPM == "PM" && hours<12) hours = hours+12;
        if(AMPM == "AM" && hours==12) hours = hours-12;
        var sHours = hours.toString();
        var sMinutes = minutes.toString();
        if(hours<10) sHours = "0" + sHours;
        if(minutes<10) sMinutes = "0" + sMinutes;
        return sHours + ":" + sMinutes
    }
    function subjectFilter(){
         var checked_opts = $('#sub_opts').find('.fil_opts:selected');
         var un_checked = $('#sub_opts').find('.fil_opts').not(':selected');
    
         var checked_opts_grade =$('#grade_opts').find('.fil_opts:selected');
         var un_checked_grade = $('#grade_opts').find('.fil_opts').not(':selected');
       
        count_box = $('#sub_opts').children('option').length ;
        grade_box =  $('#grade_opts').children('option').length ;

    
        //getting month filter data
        var month_active_fil = $('#filters_div').find('button.fil_active');
        var month_fil_data = '';
        if(month_active_fil.length!=0){
            month_fil_data = month_active_fil.data('filter');
        }
    
        var grade_fil_data='';
         if(checked_opts_grade.length!=0){
             _.each(checked_opts_grade,function(u){
                 grade_fil_data +=  $(u).data('value')+' ';
        });
            }
    
            if(checked_opts.length==0 && checked_opts_grade.length == 0){
                if (month_fil_data.indexOf('All')>-1){
                    var months = ['January','February','March', "April","May","June","July","August","September","October","November","December"];
                    _.each(months,function(uu){
                        $('.mix'+'.'+uu+filter_years).fadeIn(500);
                    });
                }else{
                    $('.mix'+month_fil_data).fadeIn(500);
                    $('.mix'+sub_fil_data).fadeIn(500);
                }
           /* $('.mix'+grade_fil_data).fadeIn(500);*/
            }else{
    
                if((checked_opts.length == count_box || un_checked.length == count_box ) &&
                 (checked_opts_grade.length  == grade_box || un_checked_grade.length == grade_box)) {
                     _.each(checked_opts,function(u){
                             sub_fil_data1 = $(u).data('value')+' ';
                             $('.'+sub_fil_data1).fadeIn(500);
                      });
    
                _.each(checked_opts_grade,function(u){
                        grade_fil_data = $(u).data('value')+' ';
                        $('.'+grade_fil_data).fadeIn(500);
                    });
                }
                else if((checked_opts.length == count_box ) && (checked_opts_grade.length == 1)){
                _.each(checked_opts_grade,function(u){
                        grade_fil_data = $(u).data('value')+' ';
                        $('.'+grade_fil_data).fadeIn(500);
                    });

                }
                else if(un_checked.length == count_box && un_checked_grade.length == grade_box){
                    _.each(un_checked_grade,function(u){
                        ungrd_fil_data = $(u).data('value')+' ';
                        $('.'+ungrd_fil_data).fadeOut(500);
                    });
                    _.each(un_checked,function(u){
                         unsub_fil_data1 = $(u).data('value')+' ';
                         $('.'+unsub_fil_data1).fadeOut(500);
                     });

                }
                else{
                 if(un_checked.length < count_box && checked_opts.length < count_box ) {
                _.each(checked_opts,function(u){
                     var  sel_sub =  $(u).data('value');
                     $('.'+sel_sub).fadeIn(500);
                    });
                     _.each(un_checked,function(u){
                     var  sel_sub =  $(u).data('value');
                     $('.'+sel_sub).fadeOut(500);
                     });

                    }
                    if(un_checked_grade.length < grade_box) {
                    _.each(un_checked_grade,function(u){
                        ungrd_fil_data = $(u).data('value')+' ';
                        $('.'+ungrd_fil_data).fadeOut(500);
                    });
                    }
                     if(checked_opts_grade.length < grade_box) {
                    _.each(checked_opts_grade,function(u){
                        grade_fil_data = $(u).data('value')+' ';
                        $('.'+grade_fil_data).fadeIn(500);
                    });
                    }
                    if(un_checked.length < count_box) {
                     _.each(un_checked,function(u){
                         unsub_fil_data1 = $(u).data('value')+' ';
                         $('.'+unsub_fil_data1).fadeOut(500);
                     });
                   }

                }

            }
    }
    function gradeFilter(){
        var checked_opts = $('#grade_opts').find('.fil_opts:selected');
        var un_checked = $('#grade_opts').find('.fil_opts').not(':selected');
    
        count_box = $('#sub_opts').children('option').length ;
        grade_box =  $('#grade_opts').children('option').length ;
    
    
        //getting subject filter data
        var checked_opts_sub = $('#sub_opts').find('.fil_opts:selected');
        var un_checked_sub = $('#sub_opts').find('.fil_opts').not(':selected');
    
        var sub_fil_data='';
         if(checked_opts_sub.length!=0){
             _.each(checked_opts_sub,function(u){
                 sub_fil_data +=  $(u).data('value')+' ';
        });
            }
        //getting month filter data
        var month_active_fil = $('#filters_div').find('button.fil_active');
        var month_fil_data = '';
        if(month_active_fil.length!=0){
            month_fil_data = month_active_fil.data('filter');
        }
            if(checked_opts.length== grade_box || un_checked.length == grade_box){
                $('.mix'+month_fil_data).fadeIn(500);
    //        	$('.mix'+sub_fil_data).fadeIn(500);
                 _.each(checked_opts,function(u){
                        grade_fil_data = $(u).data('value')+' ';
                        $('.'+grade_fil_data).fadeIn(500);
                    });
    
                     _.each(un_checked,function(u){
                        ungrd_fil_data = $(u).data('value')+' ';
                        $('.'+ungrd_fil_data).fadeIn(500);
                    });
            } else {
    
                if(checked_opts.length < grade_box && un_checked.length <grade_box) {
                 _.each(checked_opts,function(u){
    
                     var  sel_grd =  $(u).data('value');
                          $('.'+sel_grd).fadeIn(500);
                });
    
                 _.each(un_checked,function(u){
    
                     var  sel_grd =  $(u).data('value');
                          $('.'+sel_grd).fadeOut(500);
                });
                }
                 if(checked_opts_sub.length < count_box) {
                     _.each(checked_opts_sub,function(u){
                             sub_fil_data1 = $(u).data('value')+' ';
                             $('.'+sub_fil_data1).fadeIn(500);
                      });
                 }
                if(un_checked_sub.length < count_box) {
                _.each(un_checked_sub,function(u){
                    unsub_fil_data1 = $(u).data('value')+' ';
                    $('.'+unsub_fil_data1).fadeOut(500);
                });
               }
                if(un_checked.length < grade_box) {
                     _.each(un_checked,function(u){
                          var  sel_grd =  $(u).data('value');
                          $('.'+sel_grd).fadeOut(500);
                    });
                    }
                }
    
    }
    
    }); //document ready end