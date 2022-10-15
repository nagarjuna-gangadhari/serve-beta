$(document).ready(function() {
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    var get_future_date = function(curr_date, offset_month){
        return new Date(curr_date.setMonth(curr_date.getMonth() + offset_month));
    };
    var render_events = function(month){
        $.get("/get_events/?month="+month,function(resp){
            var user_sessions = resp[0].user_sessions,
                other_sessions = resp[0].other_sessions;
            var event_html = "<li>${grade} ${subject} ${center} - ${start}</li>";
            $.template("event_template", event_html);
            if(user_sessions.length > 0){
                $("#calendar").append("<div class='user_sessions'><p>Your classes</p><ul></ul></div>");
                $.tmpl("event_template", user_sessions).appendTo("div.user_sessions ul");
            }
            if(other_sessions.length > 0){
                $("#calendar").append("<div class='other_sessions'><p>Other classes</p><ul></ul></div>");
                $.tmpl("event_template", other_sessions).appendTo("div.other_sessions ul");
            }
            var curr_month = calendar.fullCalendar("getDate").getMonth();
            var day_mapping = ["mon","tue","wed","thu","fri","sat","sun"];
            var pin_it = function(pin_color){
                    this.start = new Date(this.start);
                    var cur_day = this.day;
                    var cur_date = parseInt(this.date.slice(0,-6));
                    var day_cells = calendar.find(".fc-"+ day_mapping[cur_day]).not(".fc-other-month,.fc-widget-header");
                    var that = this;
                    (function(cur_date,that){
                        $.each(day_cells.find("div.fc-day-number"),function(){
                            if(parseInt($(this).text()) == cur_date){
                                var image = "<img class='pin' style='float:right;' src='/static/images/green_dot.png'/>";
                                /*if(pin_color == "green")
                                    image = "<img class='pin' style='float:right;' src='/static/images/green_dot.png'/>";*/
                                $(this).next("div.fc-day-content").children("div").append(image);
                                $(this).parents("td").attr({ "data-event-id": that.id });
                            }
                        });
                    }(cur_date,that));
            }
            $.each(user_sessions,function(i,v){
               pin_it.apply(this,["green"]);
            });
            $.each(other_sessions,function(i,v){
               pin_it.apply(this,["green"]);
            });
        });
    },
    clear_pins = function(){
        $("img.pin").remove();
        $("img.pin").parents("td").removeAttr("data-event-id");
    },
    clear_events = function(){
        $("div.user_sessions").remove();
        $("div.other_sessions").remove();
        $("div.single_sessions").remove();
    },
    render_event = function(id){
        $.get("/get_event/?id="+id,function(resp){
            curr_event = resp[0];
            $("#calendar").append("<div class='single_sessions'><p class='event-name'>"+ curr_event.topic +", "+ curr_event.grade +" "+ curr_event.subject +"</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left'>"+ curr_event.date +" "+ curr_event.start +", "+ curr_event.center +"</p><div style='clear:both'></div></div>");
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
                    events: [],
                }
            ],
            eventMouseover: function(event, jsEvent, view) {
                   if (view.name !== 'agendaDay') {
                        $(jsEvent.target).attr('title', event.title);
                    }
                    return false;
            },
            eventRender: function(e, ele){
                console.log(e);
                console.log(ele);
            },
            dayClick: function(date, allDay, jsEvent, view) {
                console.log(this);
                clear_events();
                if($(this).attr("data-event-id")){
                    //render_event($(this).attr("data-event-id"));
                }
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
    $("ul.custom-select li span.dropdown a").click(function(){
        $(this).parent("span.dropdown").prev().text($(this).text());
        window.location = $(this).attr("href");
    });
    $("select.make-admin").change(function(){
        var $assign_center = $("select.assign-center option:selected"),
            $assign_teacher = $("select.assign-teacher option:selected");
        if($(this).val() != "none" && $(this).siblings().eq(0).val()!= "none")
        {
           $(this).siblings("[rel='ajax-link']").fadeIn("fast").attr({"href": "assign_center?center_id="+$assign_center.val()+"&user_id="+$assign_teacher.val()});
        }
        else{
           $(this).siblings("[rel='ajax-link']").fadeOut("fast").attr({"href": ""});

        }
    });
});

