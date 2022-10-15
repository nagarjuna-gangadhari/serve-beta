$(document).ready(function(){

window.pref_med= $(".med").attr("id");
window.usr_status= $(".usr").attr("id");
$("#demand_message_alert").addClass('hide');
$("input[type=checkbox][data-value="+pref_med+"]").prop("checked",true);

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





window.sr = ScrollReveal();
sr.reveal('.thumbnail');


var loading = function() {
        // add the overlay with loading image to the page
        var over = '<div id="overlay">' +
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
        var filter_days = $('#filter_days').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_days,function(u){
           sel_days.push($(u).data('value'));
        });
        var sel_slots = $('#sel_timerange').val();
        var filter_langs = $('#filter_langs').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_langs,function(u){
           language_flag = 0;
           if(pref_med != $(u).data('value')){
                language_flag = 1;
           }
           sel_langs.push($(u).data('value'));
        });
        if((language_flag == 1) && (usr_status=="true")){
            $("#demand_alert").hide();
            $("#medium_alert").removeClass("hidden");
            //alert("Your preferred language is not matching your filter");
        }
        else if((language_flag != 1) && (usr_status=="true")){
            $("#demand_alert").show();
            $("#medium_alert").addClass("hidden");
        }
        return [sel_days,sel_slots,sel_langs]
};

$(".fil_opts").click(function(){
    refresh_data();
});


// Month filter relative to subject filter
$('#filters_div').on('click','button.filter',function(event){
    //Getting subject filter data
    var checked_opts = $('#sub_opts').find('.fil_opts:checked');
    var sub_fil_data = '';
    if(checked_opts.length!=0){
        _.each(checked_opts,function(u){
            sub_fil_data += '.'+$(u).data('value');
        });
    }
    var that= $(this);
    $(this).addClass('fil_active').siblings().not(that).removeClass('fil_active');
    var sel_class = that.data('filter');
    $(sel_class).siblings().fadeOut(500);
    $(sel_class+sub_fil_data).fadeIn(500);
    $('.thumbnail').attr('style','');
});



// Subject filter 
$("#sub_opts").on('click','.fil_opts',function(){
    var checked_opts = $('#sub_opts').find('.fil_opts:checked');
    //getting month filter data
    var month_active_fil = $('#filters_div').find('button.fil_active');
    var month_fil_data = '';
    if(month_active_fil.length!=0){
        month_fil_data = month_active_fil.data('filter');
    }
        if(checked_opts.length==0){
        $('.mix'+month_fil_data).fadeIn(500);
        }else{
            var un_checked = $('#sub_opts').find('.fil_opts').not(':checked');
             _.each(un_checked,function(u){
                 var  sel_sub =  $(u).data('value');
                 $('.'+sel_sub).fadeOut(500);
        });
             _.each(checked_opts,function(u){
                 var  sel_sub =  $(u).data('value');
                 $('.'+sel_sub+month_fil_data).fadeIn(500);
                 console.log('.'+sel_sub+month_fil_data);
        });
        }

});

var refresh_data  =  function()
    {
            var fil_data = get_filter_data();
            loading();
            var csrftoken = getCookie('csrftoken');
            if( (fil_data[0]).length < 2 ){
                $('#demand_alert').removeClass('hide');
            }else{
                $('#demand_alert').addClass('hide');
            }
            $('#filter_days,#filter_times').tooltip('hide');
            $.post('/get_demand/',{'csrfmiddlewaretoken':csrftoken,'sel_days':JSON.stringify(fil_data[0]),'sel_langs':JSON.stringify(fil_data[2]),'sel_slots':JSON.stringify(fil_data[1])},function(resp){
            resp9=resp;
            var demand_template = _.template("<% _.forEach(resp9.data,function(u){%>" +
                                 "<% if (u.pending_courses > 0) {%><div class='col-xs-12 col-sm-6 col-md-4 mix <% _.forEach(u.tags.subjects,function(uu){     %> <%=uu%> <% })%> <% _.forEach(u.tags.months,function(um){     %> <%=um%> <% })%>' >"+
                                    "<% if (window.usr_status=='true') {%><a href='/demand_detail/<%=u.id%>/' style='text-decoration:none;'><%}else {%><a data-toggle='modal'data-target='#login-modal'id='login-trigger' class='already'style='cursor:pointer;text-decoration:none'><% } %> <div class='thumbnail ' >"+
                                        "<img class='thumb-img img-responsive' src='<%=u.image%>' alt='...'>"+
                                        "<div class='caption' style='background-color:white'>"+
                                            "<h3><%=u.title%></h3>"+
                                            "<p><%=u.description%></p>"+
                                        "</div>"+
                                        " <div class='row thumb_row' >"+
                                            "<div class='col-xs-12 col-sm-6 stat_left'>"+
                                                "<%=u.running_courses%> teachers teaching"+
                                            "</div>"+
                                            "<div class='col-xs-12 col-sm-6 stat'>"+
                                                "<%=u.pending_courses%> more needed"+
                                            "</div>"+
                                        "</div>"+
                                    "</div></a>"+
                                "</div><% } %>"+
                                "<% }) %>");
            filter_subs = [];
            filter_months = [];
            _.forEach(resp9.data, function(u){
                    filter_subs = (_.union(u.tags.subjects,filter_subs));
                    filter_months = (_.union(u.tags.months,filter_months));
            });
            //month sort
            var allMonths = ['January','February','March', "April","May","June","July","August","September","October","November","December"];
            filter_months.sort(function(a,b){
                return allMonths.indexOf(a) > allMonths.indexOf(b);
            });
            var filter_template = _.template("<div class='col-xs-12 col-sm-12 col-md-12 col-lg-12'>"+
                                            "<div class='row fil_rw' >"+
                                            "<h4>Courses starting from</h4>"+
                                            "<hr style='margin:5px !important'>"+
                                            "<% _.forEach(filter_months,function(u){%>"+
                                                    "<button class='filter  btn-link' style='font-size:14px;' data-filter='.<%= u %>'><%=u%></button>"+
                                            "<% }) %>"+
                                            "</div>"+
                                            "</div>");
            var subj_filter = _.template("<% _.forEach(filter_subs,function(u){%>"+
                    "<div class='checkbox'>"+
                       " <label class='demand_label'>"+
                            "<input type='checkbox' data-value='<%=u%>' class='fil_opts'><%=u%>"+
                        "</label>"+
                    "</div>"+
                    "<% }) %>");
            demand_template(resp9.data);
            console.log(resp9.data);
            subj_filter(resp9.data);
            filter_template(filter_subs);
            if(resp9.data.length == 0){
                $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Schools Matching Your filters..!</p>')
            }else{
                $('#thumbs_div').html(demand_template);
            }
            $('#filters_div').html(filter_template);
            $('#sub_opts').html(subj_filter);
            window.sr = ScrollReveal();
            sr.reveal('.thumbnail');
            }).done(function(){
            	
            });
    }

// Time picker JS

$("#slider-range").slider({
    range: true,
    min: 420,
    max: 1140,
    step: 15,
    values: [540, 1020],
    change: function (e, ui) {
        var hours1 = Math.floor(ui.values[0] / 60);
        var minutes1 = ui.values[0] - (hours1 * 60);

        if (hours1.length == 1) hours1 = '0' + hours1;
        if (minutes1.length == 1) minutes1 = '0' + minutes1;
        if (minutes1 == 0) minutes1 = '00';
        if (hours1 >= 12) {
            if (hours1 == 12) {
                hours1 = hours1;
                minutes1 = minutes1 + " PM";
            } else {
                hours1 = hours1 - 12;
                minutes1 = minutes1 + " PM";
            }
        } else {
            hours1 = hours1;
            minutes1 = minutes1 + " AM";
        }
        if (hours1 == 0) {
            hours1 = 12;
            minutes1 = minutes1;
        }



        $('.slider-time').html(hours1 + ':' + minutes1);

        var hours2 = Math.floor(ui.values[1] / 60);
        var minutes2 = ui.values[1] - (hours2 * 60);

        if (hours2.length == 1) hours2 = '0' + hours2;
        if (minutes2.length == 1) minutes2 = '0' + minutes2;
        if (minutes2 == 0) minutes2 = '00';
        if (hours2 >= 12) {
            if (hours2 == 12) {
                hours2 = hours2;
                minutes2 = minutes2 + " PM";
            } else if (hours2 == 24) {
                hours2 = 11;
                minutes2 = "59 PM";
            } else {
                hours2 = hours2 - 12;
                minutes2 = minutes2 + " PM";
            }
        } else {
            hours2 = hours2;
            minutes2 = minutes2 + " AM";
        }

        $('.slider-time2').html(hours2 + ':' + minutes2);
        var start_time = get_24hrtime(hours1 + ':' + minutes1);
        var end_time = get_24hrtime(hours2 + ':' + minutes2);
        $('#sel_timerange').val(start_time+';'+end_time);
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


}); //document ready end