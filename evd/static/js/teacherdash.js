$(document).ready(function() {

    var today_date = new Date();
    var d = today_date.getDate();
    var m = today_date.getMonth();
    var y = today_date.getFullYear();
    window.render_event_done = true;
    var get_future_date = function(curr_date, offset_date) {
	return new Date(curr_date.setDate(curr_date.getDate() + offset_date));
    };

    var day_index = today_date.getDay();

    if(day_index == 1)
	    var offset_date = 6;
    else if(day_index == 2)
	    var offset_date = 5;
    else if(day_index == 3)
	    var offset_date = 4;
    else if(day_index == 4)
	    var offset_date = 3;
    else if(day_index == 5)
	    var offset_date = 2;
    else if(day_index == 6)
	    var offset_date = 1;
    else if(day_index == 7)
	    var offset_date = 7;

    var future_date = get_future_date(today_date, offset_date);
    var week_date = new Date(future_date.getTime()+31800000);
    var today_date = new Date();

    render_events = function(month){
    month = ( month%12 !=0 ? month%12 : 12);

    $.get("/get_events/?month="+month,function(resp){
        var user_sessions = resp[0].user_sessions,
            other_sessions = resp[0].other_sessions;

        var curr_month = calendar.fullCalendar("getDate").getMonth();
        var day_mapping = ["mon","tue","wed","thu","fri","sat","sun"];

        window.dates_arr = [];

        var pin_it = function(pin_color){
                var cur_day = this.day;
                var cur_date = parseInt(this.date.slice(0,-6));
                var day_cells = calendar.find(".fc-"+ day_mapping[cur_day]).not(".fc-other-month,.fc-widget-header");
                var that = this;
                dates_arr[dates_arr.length] = cur_date;

                $.each(day_cells.find("div.fc-day-number"),function(){
                    if(parseInt($(this).text()) == cur_date){
                        var image = null;

                        if(pin_color == "green" && !$(this).next("div.fc-day-content").find("img.green-pin").length > 0)
                            image = "<img class='pin green-pin' style='float:right;' src='/static/images/green_dot.png'/>";

                        else if(pin_color == "red" && !$(this).next("div.fc-day-content").find("img.red-pin").length > 0)
                            image = "<img class='pin red-pin' style='float:right;' src='/static/images/red_dot.png'/>";

                        if(image)
                            $(this).next("div.fc-day-content").children("div").append(image);
                    }
                });
        }

        var d = function(dates_arr){
                var results = [];

                $.each(dates_arr, function(i, el){

                    if($.inArray(el, results) === -1) results.push(el);
                });

                for(var i in results){
                    var cur_date = results[i];

                    if(cur_date == today_date.getDate() && month == today_date.getMonth()+1){
                        clear_events();
                        $(".fc-today .fc-day-number").each(function(){
                            if(Number($(this).text()) == cur_date){
                                render_event(today_date);
                            }
                        });
                    }
                }
        }

        var first_day_events = function(){

                if(month != today_date.getMonth()+1){
                    var done_request = [],
                        first_day = 1;
                    $(".fc-day-number").each(function(){

                        if(Number($(this).text()) == first_day){
                            var first_date = new Date(calendar.fullCalendar("getDate").getFullYear(), calendar.fullCalendar("getDate").getMonth(), 1);
                            if ($.inArray(first_day, done_request) === -1){
                                render_event(first_date);
                                done_request.push(first_day)
                            }
                        }
                    });
                }
        };

        $.each(user_sessions,function(i,v){
           pin_it.apply(this,["green"]);
        });

        $.each(other_sessions,function(i,v){
//           pin_it.apply(this,["red"]);
        });

        d(dates_arr);
        first_day_events();
    });
    },
    clear_pins = function(){
    	$("img.pin").remove();
    },

    clear_events = function(){
	$("div.user_sessions").remove();
	$("div.other_sessions").remove();
	$("div.single_sessions").remove();
	$("div.date-header").remove();
	$("div.classroom").remove();
	$("div.session").remove();
	$(".feedback-modal").remove();
	$(".attendance-modal").remove();
    },

    render_event = function(date){

    if(render_event_done) {

        $.get("/get_event/?day="+date,function(resp){
            render_event_done = true;
            clear_events();
            var curr_events = resp[0];
            var curr_event = null,
                pin = null;
            var day_index = date.getDay();
            var day_mapping = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            var month_mapping = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            if(day_index == 7)
                var day = day_mapping[0];
            else
                var day = day_mapping[day_index];

            var month = month_mapping[date.getMonth()];
            if (resp[0].user_sessions != null && resp[0].user_sessions != ''){
            	$("#calendar").append("<div class='date-header'><p>" + day + ", " + month + " " + date.getDate() +"</p></div>");
        	}
            for(var index in curr_events.user_sessions) {
                curr_event = curr_events.user_sessions[index];
                window.curr_session_id = curr_event.id;
                curr_event = curr_events.user_sessions[index];
                var topics = curr_event.topic;
                var $topics_html = "";

                for(var i in topics){
                    var topic = topics[i];

                    if(topic.url != "")
                        $topics_html += "<a target='_blank' href='"+topic.url +"'>"+topic.title + " " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                    else
                        $topics_html += "<a href='#'>"+topic.title +", " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                }

               $("#calendar").append("<div class='session'><div class='single_sessions user_session'><div style='float:left;'><p>" + curr_event.start + "</p></div><div style='margin-left:17px;float:left;margin-top:-3px;width:260px;'><p class='event-name'>"+ $topics_html + "</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left;font-size:11px;'>" + "by "+ curr_event.teacher + " at <a class='center' href='#center-modal' data-toggle='modal' data-centerid='"+curr_event.center_id+"'>"+ curr_event.center +"</a><span class='session_status'> ("+curr_event.session_status+")</span></p><div style='clear:both'></div></div></div></div>");

             var $attendance_modal = $('<div id="attendance'+ curr_session_id +'" class="attendance-modal modal hide" style="max-height:600px;"><img style="display:block;margin:10px auto" src="/static/images/loader.gif"/></div>');

             var $feedback_modal = $('<div id="feedback-'+ curr_session_id +'" class="feedback-modal modal hide" style="width:615px;"><img style="display:block;margin:10px auto" src="/static/images/loader.gif"/></div>');

                $("#calendar").append($attendance_modal).append($feedback_modal);

                (function(curr_session_id, $feedback_modal, $attendance_modal){
                    $attendance_modal.on('show',function(){
                        if($(this).children("img").length > 0 ){
                            var $that = $(this);
                            $.get("/get_attendance?session="+curr_session_id,function(resp){
                                $that.children("img").remove();
                                $that.append(resp);
                                $that.find("[rel='submit']").click(evd.ajax_submit);
                            }); 
                        }
                    });
                    $("#feedback-"+ curr_session_id).on('show',function(){
                        if($(this).children("img").length > 0 ){
                            var $that = $(this);
                            $.get("/get_feedback?session="+curr_session_id,function(resp){
                                $that.children("img").remove();
                                $that.append(resp);
                                $that.find("[rel='submit']").click(evd.ajax_submit);
                            }); 
                        }
                    });

                }(curr_session_id, $feedback_modal, $attendance_modal));
            }

            for(var index in curr_events.other_sessions) {
                curr_event = curr_events.other_sessions[index];
                window.curr_session_id = curr_event.id;
                var topics = curr_event.topic;
                var $topics_html = "";
                for(var i in topics){
                    var topic = topics[i];
                    if(topic.url != "")
                        $topics_html += "<a target='_blank' href='"+topic.url +"'>"+topic.title + " " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                    else
                        $topics_html += "<a href='#'>"+topic.title +", " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                }

//                $("#calendar").append("<div class='session'><div class='single_sessions other_session'><div style='float:left;'><p>" + curr_event.start + "</p></div><div style='margin-left:17px;float:left;margin-top:-3px;width:260px;'><p class='event-name'>"+ $topics_html + "</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left;font-size:11px;'>" + "by "+ curr_event.teacher + " at <a class='center' href='#center-modal' data-toggle='modal' data-centerid='"+curr_event.center_id+"'>"+ curr_event.center +"</a><span class='session_status'> ("+curr_event.session_status+")</span></p><div style='clear:both'></div></div></div></div>");
            }

        }).error(function(){
            render_event_done = true;
        });
        render_event_done = false;
    }
    };

    window.calendar = $("#calendar").fullCalendar({
        theme: false,
        header: {
                left: 'prev',
                center: 'title',
                right: 'next'
        },
        selectable: true,
        editable: true,
        dragOpacity: 0.2,
        columnFormat: {
                    month: 'ddd',    // Mon
                    week: 'ddd d/M', // Mon 9/7
                    day: 'dddd d/M'  // Monday 9/7
        },
        eventSources: [
            {
                events: []
            }
        ],
        eventMouseover: function(event, jsEvent, view) {
               if (view.name !== 'agendaDay') {
                    $(jsEvent.target).attr('title', event.title);
                }
                return false;
        },
        eventRender: function(e, ele){
        },
        dayClick: function(date, allDay, jsEvent, view) {
            clear_events();
            render_event(date);
            return false;
        }
    });
    var loaded_month = calendar.fullCalendar("getDate").getMonth() + 1;
	    render_events(loaded_month);
	    $("td.fc-header-left > span.fc-button").click(function(){
	    clear_pins();
	    clear_events();
	    render_events(--loaded_month);
    });
    $("td.fc-header-right > span.fc-button").click(function(){
	    clear_pins();
	    clear_events();
	    render_events(++loaded_month);
    });
    $("[rel=tooltip]").tooltip();
    $(".dashboard-calendar-container").on('change','#status',function(e){
	e.preventDefault();
	var stat = $(this).val(),
	    res_code = $(this).parents('.drop-downs').next('.reason-code');
	if(stat === 'Cancelled' || stat === 'Rescheduled'){
	    res_code.removeClass('hide');
	}else{
	    res_code.addClass('hide');
	}
    });
    $('.attendence-board > select').change(function(){

	var name=  $(this).attr('name');
	var $board = $('.attendence-board')

	if(name === 'my_offerings'){
	    var offering_Id = $(this).val(),
		options = $board.find('select[name="'+offering_Id+'"]').children('option').clone();
	    $board.find("select[name='my_students']").empty().append(options);
	    $board.children('.student_info').addClass('hide').find('tbody').html('');
	}else if(name === 'my_students'){
	    var id = $(this).val();
	    var temp = "<tr><td>${subject}</td><td>${present}/${total}</td><td>${absent}/${total}</td></tr>";
	    if(id){
		$.get("/attendance_mystudents/?id="+id,function(resp){
		    if(resp.length > 0)
			$board.children('.student_info').addClass('hide').removeClass('hide').find('tbody').html('');
		    else
			$board.children('.student_info').addClass('hide');
		    $.each(resp,function(i,obj){
			$board.children('.student_info').find('tbody').append('<tr></tr>');
			$(temp).tmpl(obj).appendTo($board.children('.student_info').find('tbody > tr:last-child'));
		    });
		});
	    }else{
		$board.children('.student_info').addClass('hide');
	    }
	}
    });

    $(".assigned_offering").children("ul").children("li").each(function(){

	$(".assigned_offering").children("ul").children("li").click(function(){
	   var offering = $(this).children("p").text();

	   $(".students-assigned").children("h4").each(function(){
		var offer = $(this).text();

		if(offering == offer){
		    $(".students-assigned").hide();
		    $(this).parents(".students-assigned").show();
		}
	   });
	});
    });

    $("li.dropdown, ul.dropdown-menu").mouseenter(function(){
	$(this).children("ul.dropdown-menu").show();
    });

    $("li.dropdown, ul.dropdown-menu").mouseleave(function(){
	$(this).children("ul.dropdown-menu").hide();
    });
    
});

