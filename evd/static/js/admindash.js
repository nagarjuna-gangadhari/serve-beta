        $(document).ready(function() {
                var today_date = new Date();
                var d = today_date.getDate();
                var m = today_date.getMonth();
                var y = today_date.getFullYear();
                window.render_event_done = true;
                var get_future_date = function(curr_date, offset_date){
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
                var curr_date = new Date();
                var today_date = new Date();
                var render_events = function(month){
                    month = ( month%12 !=0 ? month%12 : 12);
                    $.get("/get_events/?month="+month,function(resp){
                        var user_sessions = resp[0].user_sessions,
                            other_sessions = resp[0].other_sessions;
                        user_sessions = user_sessions.concat(other_sessions);
                        other_sessions = [];
                        /*if(user_sessions.length > 0){
                            $("#calendar").append("<div class='user_sessions'><p></p><ul></ul></div>");
                            //$.tmpl("event_template", user_sessions).appendTo("div.user_sessions ul");
                        }
                        if(other_sessions.length > 0){
                            $("#calendar").append("<div class='other_sessions'><p>Other classes</p><ul></ul></div>");
                            //$.tmpl("event_template", other_sessions).appendTo("div.other_sessions ul");
                        }*/
                        var curr_month = calendar.fullCalendar("getDate").getMonth();
                        var day_mapping = ["mon","tue","wed","thu","fri","sat","sun"];
                        window.dates_arr = [];
                        var pin_it = function(pin_color){
                                var cur_day = this.day;
                                var cur_date = parseInt(this.date.slice(0,-6));
                                var day_cells = calendar.find(".fc-"+ day_mapping[cur_day]).not(".fc-other-month,.fc-widget-header");
                                var that = this;
                                //var event_html = "<li>" + this.grade + " " + this.subject + " " + this.center + " - " + this.date + ", " + this.start + "</li>";
                                dates_arr[dates_arr.length] = cur_date;
                                /*if(cur_date >= 1 && cur_date <= 7)
                                    $(event_html).appendTo("div.user_sessions ul");*/
                                (function(cur_date,that){
                                    $.each(day_cells.find("div.fc-day-number"),function(){
                                        if(parseInt($(this).text()) == cur_date ){
                                            var image = null;

                                            if(pin_color == "green" && !$(this).next("div.fc-day-content").find("img.green-pin").length > 0)
                                                image = "<img class='pin green-pin' style='float:right;' src='/static/images/green_dot.png'/>";

                                            else if(pin_color == "red" && !$(this).next("div.fc-day-content").find("img.red-pin").length > 0)
                                                image = "<img class='pin red-pin' style='float:right;' src='/static/images/red_dot.png'/>";

                                            if(image)
                                                $(this).next("div.fc-day-content").children("div").append(image);
                                        }
                                    });
                                }(cur_date,that));

                            }
                        var d = function(dates_arr){
                                var results = [];
                                $.each(dates_arr, function(i, el){
                                    if($.inArray(el, results) === -1) results.push(el);
                                })
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
                                    clear_events();
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
                        d(dates_arr);
                        first_day_events();
                        $.each(other_sessions,function(i,v){
                           pin_it.apply(this,["red"]);
                        });
                    });
                },
                clear_pins = function(){
                    $("img.pin").remove();
                },
                clear_events = function(){
                    $("div.user_sessions").remove();
                    $("div.other_sessions").remove();
                    $("div.single_sessions").remove();
                    $("div.classroom").remove();
                    $("div.date-header").remove();
                    //$("div.header").remove();
                    $("div.session").remove();
                },
                render_event = function(date){
                    $.get("/get_event/?day="+date,function(resp){
                        var curr_events = resp[0];
                        curr_events = curr_events.user_sessions.concat(curr_events.other_sessions)
                        var curr_event = null;
                        var day_index = date.getDay();
                        var day_mapping = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                        var month_mapping = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                        if(day_index == 7)
                            var day = day_mapping[0];
                        else
                            var day = day_mapping[day_index];
                        var month = month_mapping[date.getMonth()];
                        /*$("#calendar").append("<div class='header' style='font-size: 18px;padding-bottom:10px; color: #f15a22; text-align: center;'><p>Classroom Corner</p></div>");*/
                        $("#calendar").append("<div class='classroom'><pre><br /><h3><strong>    My Classroom</strong></h3><br /></pre></div>").append("<div class='date-header'><p>" + day + ", " + month + " " + date.getDate() +"</p></div>");
                      /*  $("#calendar").append("<div class='classroom'><pre><br />My Classroom<br /></pre><div class='date1-header'><p>" + day + ", "           + month + " " + date.getDate() +"</p></div></div>");*/

                        for(var index in curr_events){
                            curr_event = curr_events[index];
                            var topics = curr_event.topic;
                                var $topics_html = "";
                                for(var i in topics){
                                    var topic = topics[i];
                                    if(topic.url != "")
                                        $topics_html += "<a target='_blank' href='"+topic.url +"'>"+topic.title + " " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                                    else
                                        $topics_html += "<a href='#'>"+topic.title +", " + curr_event.grade + " "  + curr_event.subject + "</a> " ;
                                }
                            $("#calendar").append("<div class='session'><div class='single_sessions user_session'><div style='float:left;'><p>" + curr_event.start + "</p></div><div style='margin-left:17px;float:left;margin-top:-3px;width:260px;'><p class='event-name'>"+ $topics_html + "</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left;font-size:11px;'>" + "by <a class='teacher' href='#teacher-modal' data-toggle='modal' data-teacherid='"+curr_event.teacher_id+"'>" + curr_event.teacher + "</a> at <a class='center' href='#center-modal' data-toggle='modal' data-centerid='"+curr_event.center_id+"'>"+ curr_event.center +"</a><span class='session_status'> ("+curr_event.session_status+")</span></p><div style='clear:both'></div></div></div></div>");
                        }
                    });
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
                $("ul.custom-select li").toggle(function(){
                    $("ul.custom-select > li.focus-f").not($(this)).trigger("click");
                    $(this).addClass("focus-f");
                },function(){
                    $(this).removeClass("focus-f");
                });
                $("html").click(function(){
                    $("ul.custom-select li.focus-f").trigger("click");
                });
                $(".dashboard-notifications-container .note-box ul.custom-select li span.dropdown a").click(function(){
                    $(this).parent("span.dropdown").prev().text($(this).text());
                    window.location = $(this).attr("href");
                });
                $("select.make-admin").change(function(){
                    var $assign_center = $("select.assign-center option:selected"),
                        $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    if($(this).val() != "None" && $(this).siblings().eq(0).val()!= "None")
                    {
                    	 
                         $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                    }
                    else{
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                });

                $("select.assign-center").change(function(){
                    var $assign_center = $("select.assign-center option:selected");
                    var selected_index = $(this).children(":selected").index(),
                        selected = $(this).children(":selected"),
                        selected_sibling = $(this).siblings().eq(0).children().eq(selected_index);
                    $(this).siblings().eq(1).children().removeAttr("selected");
                    if(center_map[selected.text()] == undefined ){
                        $(this).siblings().eq(1).children("option[value='None']").attr({"selected": "selected"});
                        $(this).siblings().eq(1).attr("title","Select Admin");
                    }
                    else{
                        $(this).siblings().eq(1).children("[data-related='"+center_map[selected.text()]+"']").attr({"selected": "selected"});
                        $(this).siblings().eq(1).attr("title",""+center_map[selected.text()]+"");
                    }
                    if(center_assistant_map[selected.text()] == undefined ){
                        $("select.assign-assistant").children("option[value='None']").attr({"selected": "selected"});
                        $('.assign-assistant').attr("title","Select Assistant");
                    }
                    else{
                        $("select.assign-assistant").children("[data-related='"+center_assistant_map[selected.text()]+"']").attr({"selected": "selected"});
                    	$('.assign-assistant').attr("title",""+center_assistant_map[selected.text()]+"");
                    }
                    if(center_partner_map[selected.text()] == undefined ){
                        $("select.assign-partner").children("option[value='None']").attr({"selected": "selected"});
                        $('.assign-partner').attr("title","Select Partner");
                    }
                    else{
                        $("select.assign-partner").children("[data-related='"+center_partner_map[selected.text()]+"']").attr({"selected": "selected"});
                        $('.assign-partner').attr("title",""+center_partner_map[selected.text()]+"");
                    }
                    if(center_orgpartner_map[selected.text()] == undefined ){
                        $("select.assign-orgpartner").children("option[value='None']").attr({"selected": "selected"});
                        $('.assign-orgpartner').attr("title","Select Org Partner");
                    }
                    else{
                        $("select.assign-orgpartner").children("[data-related='"+center_orgpartner_map[selected.text()]+"']").attr({"selected": "selected"});
                        $('.assign-orgpartner').attr("title",""+center_orgpartner_map[selected.text()]+"");
                    }
                    if(center_fieldCoordinator_map[selected.text()] == undefined ){
                        $("select.assign-field").children("option[value='None']").attr({"selected": "selected"});
                        $('.assign-field').attr("title","Select Field Coordinator");
                    }
                    else{
                        $("select.assign-field").children("[data-related='"+center_fieldCoordinator_map[selected.text()]+"']").attr({"selected": "selected"});
                        $('.assign-field').attr("title",""+center_fieldCoordinator_map[selected.text()]+"");
                    }
                    if(center_deliveryCoordinator_map[selected.text()] == undefined ){
                        $("select.assign-delivery").children("option[value='None']").attr({"selected": "selected"});
                        $('.assign-delivery').attr("title","Select Delivery Coordinator");
                    }
                    else{
                        $("select.assign-delivery").children("[data-related='"+center_deliveryCoordinator_map[selected.text()]+"']").attr({"selected": "selected"});
                        $('.assign-delivery').attr("title",""+center_deliveryCoordinator_map[selected.text()]+"");
                    }
                    var $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    window.center_admin_value = $assign_teacher.val();
                    window.center_assistant_value = $assign_assistant.val();
                    window.center_fieldCoordinator_value = $assign_fieldCoordinator.val();
                    window.deliveryCoordinator_value = $assign_deliveryCoordinator.val();
                    window.partner_value = $assign_partner.val();
                    window.orgpartner_value = $assign_orgpartner.val();
                    if(!selected.hasClass("no-admin") || $(this).siblings().eq(1).val() == "None"){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else if(selected.hasClass("no-admin"))
                        $(this).siblings("[rel='ajax-link']").hide();
                    else {
                            $(this).siblings("[rel='ajax-link']").children("span").text("confirm").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                    }
                    var language = $assign_center.attr("data-language");
                    $("select.assign-admin").children("option").each(function(){
                        if($(this).attr("data-language") == language)
                            $(this).css({"display":"block"});
                        else
                            $(this).css({"display":"none"});
                    });
                    $("select.assign-assistant").children("option").each(function(){
                        if($(this).attr("data-language") == language)
                            $(this).css({"display":"block"});
                        else
                            $(this).css({"display":"none"});
                    });
                    if($assign_center.val() == "None"){
                        $("select.assign-admin").children("option").css({"display":"block"});
                        $("select.assign-assistant").children("option").css({"display":"block"});
                        $("select.assign-field option:selected").children("option").css({"display":"block"});
                        $("select.assign-delivery option:selected").children("option").css({"display":"block"});
                        $("select.assign-partner option:selected").children("option").css({"display":"block"});
                        $("select.assign-orgpartner option:selected").children("option").css({"display":"block"});
                    }
                    $("select.assign-admin").children("option[value='None']").css({"display":"block"});
                    $("select.assign-assistant").children("option[value='None']").css({"display":"block"});
                    $("select.assign-field option:selected").children("option[value='None']").css({"display":"block"});
                    $("select.assign-delivery option:selected").children("option[value='None']").css({"display":"block"});
                    $("select.assign-partner option:selected").children("option[value='None']").css({"display":"block"});
                    $("select.assign-orgpartner option:selected").children("option[value='None']").css({"display":"block"});
                    $assign_teacher.css({"display":"block"});
                    $assign_assistant.css({"display":"block"});
                    $assign_fieldCoordinator.css({"display":"block"});
                    $assign_deliveryCoordinator.css({"display":"block"});
                    $assign_partner.css({"display":"block"});
                    $assign_orgpartner.css({"display":"block"});
                });
                $("select.assign-admin").change(function(){
                    var $assign_center = $("select.assign-center option:selected"),
                        $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    if($assign_center.hasClass("no-admin") && $assign_teacher.val() == "None")
                        $(this).siblings("[rel='ajax-link']").hide();
                    else if($assign_teacher.val() == "None"){
                        $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
;
                        $(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                    }else if($assign_teacher.val() == center_admin_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                    	$("#adminId").attr({"href": "/assign_center?flag=Admin&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                    	$("#confirmId").attr({"href": "/assign_center?flag=Admin&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                    	$("#dcId").hide();
                    	$("#partnerId").hide();
                    	$("#orgpartnerId").hide();
                    	$("#fcId").hide();
                    	$("#assignId").hide();
                    	$("#adminId").show();
                });
                $("select.assign-assistant").change(function(){
                    var $assign_center = $("select.assign-center option:selected"),
                        $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    if($assign_assistant.val() == "None"){
                        $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
;
                        $(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                    }else if($assign_teacher.val() == center_assistant_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                		$("#assignId").attr({"href": "/assign_center?flag=Assistant&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                		$("#confirmId").attr({"href": "/assign_center?flag=Assistant&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                		$("#dcId").hide();
                    	$("#partnerId").hide();
                    	$("#orgpartnerId").hide();
                    	$("#fcId").hide();
                    	$("#adminId").hide();
                    	$("#assignId").show();
                });
                
                $("select.assign-field").change(function(){
                    var $assign_center = $("select.assign-center option:selected"),
                        $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    if($assign_fieldCoordinator.val() == "None"){
                        $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
;
                        $(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                    }else if($assign_teacher.val() == center_fieldCoordinator_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
            			$("#fcId").attr({"href": "/assign_center?flag=FieldCoordinator&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
            			$("#dcId").hide();
                    	$("#partnerId").hide();
                    	$("#orgpartnerId").hide();
                    	$("#assignId").hide();
                    	$("#adminId").hide();
                    	$("#fcId").show();
                });
                $("select.assign-delivery").change(function(){
                    var $assign_center = $("select.assign-center option:selected"),
                        $assign_teacher = $("select.assign-admin option:selected"),
                        $assign_assistant = $("select.assign-assistant option:selected");
                    	$assign_fieldCoordinator = $("select.assign-field option:selected");
                    	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                    	$assign_partner = $("select.assign-partner option:selected");
                    	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                    if($assign_deliveryCoordinator.val() == "None"){
                        $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                        $(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                    }else if($assign_teacher.val() == deliveryCoordinator_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
        				$("#dcId").attr({"href": "/assign_center?flag=DeliveryCoordinator&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
        				$("#partnerId").hide();
        				$("#orgpartnerId").hide();
                    	$("#assignId").hide();
                    	$("#adminId").hide();
                    	$("#fcId").hide();
                    	$("#dcId").show();
                });
                $("select.assign-partner").change(function(){
                	var $assign_center = $("select.assign-center option:selected"),
                    $assign_teacher = $("select.assign-admin option:selected"),
                    $assign_assistant = $("select.assign-assistant option:selected");
                	$assign_fieldCoordinator = $("select.assign-field option:selected");
                	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                	$assign_partner = $("select.assign-partner option:selected");
                	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                	if($assign_partner.val() == "None"){
                		$(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                		$(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                	}else if($assign_teacher.val() == partner_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
    					$("#partnerId").attr({"href": "/assign_center?flag=Partner&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
    					$("#partnerId").hide();
    					$("#orgpartnerId").hide();
                		$("#assignId").hide();
                		$("#adminId").hide();
                		$("#fcId").hide();
                		$("#dcId").hide();
                		$("#partnerId").show();
                	
                });
                $("select.assign-orgpartner").change(function(){
                	var $assign_center = $("select.assign-center option:selected"),
                    $assign_teacher = $("select.assign-admin option:selected"),
                    $assign_assistant = $("select.assign-assistant option:selected");
                	$assign_fieldCoordinator = $("select.assign-field option:selected");
                	$assign_deliveryCoordinator = $("select.assign-delivery option:selected");
                	$assign_partner = $("select.assign-partner option:selected");
                	$assign_orgpartner = $("select.assign-orgpartner option:selected");
                	if($assign_orgpartner.val() == "None"){
                		$(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "/assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
                		$(this).siblings("[rel='ajax-link']").children("span").text("Remove");
                	}else if($assign_teacher.val() == orgpartner_value){
                        $(this).siblings("[rel='ajax-link']").hide();
                    }
                    else
                        $(this).siblings("[rel='ajax-link']").children("span").text("confirm").attr({"href": "/assign_center?center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
    					$("#orgpartnerId").attr({"href": "/assign_center?flag=OrgPartner&center_id="+ $assign_center.val() +"&user_id="+ $assign_teacher.val()+"&assistant_id="+$assign_assistant.val()+"&fieldCoordinator_id="+$assign_fieldCoordinator.val()+"&deliveryCoordinator_id="+$assign_deliveryCoordinator.val()+"&partner_id="+$assign_partner.val()+"&orgpartner_id="+$assign_orgpartner.val()});
    					$("#orgpartnerId").hide();
    					$("#partnerId").hide();
                		$("#assignId").hide();
                		$("#adminId").hide();
                		$("#fcId").hide();
                		$("#dcId").hide();
                		$("#orgpartnerId").show();

                });
            $("li.dropdown, ul.dropdown-menu").mouseenter(function(){
                $(this).children("ul.dropdown-menu").show();
            });
            $("li.dropdown, ul.dropdown-menu").mouseleave(function(){
                $(this).children("ul.dropdown-menu").hide();
            });
            $("#calendar").on("click", ".teacher", function(){
                var teacher_id = Number($(this).attr("data-teacherid"));
                $.get("/get_teachers/?teacher_id="+teacher_id, function(resp){
                    resp = eval(resp);
                    var user_info = resp[0];
                    if(user_info.short_notes == "")
                            var title = "No notes is available";
                        else
                            var title = user_info.short_notes;
                    var $user_block = "<div class='user-block' rel='tooltip' title='"+title+"' data-placement='left'>"+
                                        "<div>"+
                                            "<div style='overflow:hidden;'>"+
                                                "<form action='/save_remarks/' method='POST' id='remarks-form' style='padding-top:10px;' data-userid='"+user_info.id+"'>{% csrf_token %}"+
                                                "<div style='overflow:hidden;background:#E6E6FA'>"+
                                                      "<img class='user-pic' src='"+user_info.picture+"' style='float:left;width:100px;height:100px'>"+
                                                      "<div class='general-information'>"+
                                                          "<p class='username'>"+user_info.name+"</p>"+
                                                          "<p style='float:right'>"+
                                                            "<select name='status' style='float:right'>"+
                                                                "<option>"+user_info.status+"</option>"+
                                                                "<option>New</option>"+
                                                                "<option>Ready</option>"+
                                                                "<option>Active</option>"+
                                                                "<option>Dormat</option>"+
                                                                "<option>Non-active</option>"+
                                                            "</select>"+
                                                          "</p>"+
                                                          "<p style='clear:both;margin-top:0px;width:340px;'>"+user_info.role+"</p>"+
                                                          "<p style='clear:both;width:130px;'><label>Medium: </label>"+user_info.medium+"</p>"+
                                                          "<p style='width:210px;'><label>Location: </label>"+user_info.location+"</p>"+
                                                          "<p><label>Avail From: </label>"+user_info.from+"</p>"+
                                                          "<p style='margin-left: -19px;'><label>Avail To: </label>"+user_info.to+"</p>"+
                                                      "</div>"+
                                                  "</div>"+
                                                "</div>"+
                                                  "<div style='width:467px;min-height:50px;font-size:small;padding:0px 10px;'>"+
                                                    "<div class='info'>"+
                                                      "<p class='email'><label>Email: </label>"+user_info.email+"</p>"+
                                                      "<p class='phone'><label>Phone: </label>"+user_info.phone+"</p>"+
                                                    "</div>"+
                                                    "<p style='margin-top:5px;'><label>Current courses: </label>"+user_info.current_courses+"</p>"+
                                                  "</div>"+
                                                  "<div class='general_info preferences' style='width:467px !important'>"+
                                                      "<p><label>Hours Contributed: </label>"+user_info.hrs_contributed+"</p>"+
                                                      "<p style='float:left'><label>Remarks: </label></p>"+
                                                      "<p style='float:left;padding-left:10px;'>"+
                                                            "<input type='hidden' name='step' value=5 />"+
                                                            "<input type='hidden' name='user_id' value='"+user_info.id+"' />"+
                                                            "<textarea class='enabled' name='remarks' rows=2 cols=50 style='width:385px !important'>"+user_info.remarks+"</textarea>"+
                                                      "</p>"+
                                                      "<a class='btn hide' data-userid='"+user_info.id+"' rel='submit' callback='after_save' href='#remarks-form' style='cursor:pointer;width:50px;font-size:12px;float:right;line-height:18px;height:20px;margin-bottom:10px;'><span class='ajax-button-label' data-loading='wait'>Save</span></a>"+
                                                  "</div>"+
                                                "</form>"+
                                              "</div>"+
                                              "<div class='preferences' style='padding:10px;float:left;width:440px;display:none'>"+
                                                  "<p><label>Preferred Courses: </label></p>"+
                                                  "<p>"+user_info.courses+"</p>"+
                                              "</div>"+
                                    "</div>"+
                                "</div>";
                    $("#teacher-modal img").hide();
                    $("#teacher-modal").append($user_block);
                    $(".user-block").on("click", ".btn", evd.ajax_submit);
                })
            });
            $("#teacher-modal").on("hide", function(){
                $("#teacher-modal .user-block").remove();
                $("#teacher-modal img").show();
            });
            var enabled = function(){
                $(this).find("a.btn").show();
            };
            $("#content").on("click", ".user-block", enabled);
            $("#html").not(".user-block").click(function(){
                $(".user-block a.btn").hide();
            });
            $("#content").on("mouseover", ".user-block", function(){
                $("[rel=tooltip]").tooltip();
            });

        });

