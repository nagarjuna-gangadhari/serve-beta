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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

$(document).ready(function() {
    $.ajaxSetup({
        // Disable caching of AJAX responses */
        cache: false
    });

    window.render_event_done = true;
    window.event_render = true;
    var today_date = new Date();
    var d = today_date.getDate();
    var m = today_date.getMonth();
    var y = today_date.getFullYear();
    var get_future_date = function(curr_date, offset_date) {
        return new Date(curr_date.setDate(curr_date.getDate() + offset_date));
    };
    var day_index = today_date.getDay();
    if (day_index == 1)
        var offset_date = 6;
    else if (day_index == 2)
        var offset_date = 5;
    else if (day_index == 3)
        var offset_date = 4;
    else if (day_index == 4)
        var offset_date = 3;
    else if (day_index == 5)
        var offset_date = 2;
    else if (day_index == 6)
        var offset_date = 1;
    else if (day_index == 7)
        var offset_date = 7;
    var future_date = get_future_date(today_date, offset_date);
    var week_date = new Date(future_date.getTime() + 31800000);
    var today_date = new Date();
    var csrf_name = $("#csrf_token input").attr("name");
    var csrf_token = $("#csrf_token input").val();
    var ay_id = $('#academic_year_id').val();
    var render_events = function(month, year) {
            month = (month % 12 != 0 ? month % 12 : 12);
            $.post("/get_offerings/", { "center_id": window.center_id, "month": month, "year": year, "csrf_name": csrf_token, 'ay_id': ay_id }, function(resp) {
                var running_courses = resp[0].running_courses,
                    pending_courses = resp[0].pending_courses,
                    others_courses = resp[0].others_courses;

                var curr_month = calendar.fullCalendar("getDate").getMonth();
                var day_mapping = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
                window.dates_arr = [];

                var pin_it = function(pin_color) {
                    var cur_day = this.day;
                    var cur_date = parseInt(this.date.slice(0, -6));
                    var day_cells = calendar.find(".fc-" + day_mapping[cur_day]).not(".fc-other-month,.fc-widget-header");
                    var that = this;
                    dates_arr[dates_arr.length] = cur_date;
                    (function(cur_date, that) {
                        $.each(day_cells.find("div.fc-day-number"), function() {
                            if (parseInt($(this).text()) == cur_date) {
                                var image = null;

                                if (pin_color == "green" && !$(this).next("div.fc-day-content").find("img.green-pin").length > 0)
                                    image = "<img class='pin green-pin' style='float:right;' src='/static/images/green_dot.png'/>";

                                else if (pin_color == "red" && !$(this).next("div.fc-day-content").find("img.red-pin").length > 0)
                                    image = "<img class='pin red-pin' style='float:right;' src='/static/images/red_dot.png'/>";

                                if (image)
                                    $(this).next("div.fc-day-content").children("div").append(image);
                            }
                        });
                    }(cur_date, that));
                }
                var d = function(dates_arr) {
                    var results = [];
                    $.each(dates_arr, function(i, el) {
                        if ($.inArray(el, results) === -1) results.push(el);
                    })
                    for (var i in results) {
                        var cur_date = results[i];
                        if (cur_date == today_date.getDate() && month == today_date.getMonth() + 1) {
                            clear_events();
                            $(".fc-today .fc-day-number").each(function() {
                                if (Number($(this).text()) == cur_date) {
                                    render_event(today_date);
                                }
                            });
                        }
                    }
                }
                var first_day_events = function() {
                    if (month != today_date.getMonth() + 1) {
                        clear_events();
                        var done_request = [],
                            first_day = 1;
                        $(".fc-day-number").each(function() {
                            if (Number($(this).text()) == firstday) {
                                var first_date = new Date(calendar.fullCalendar("getDate").getFullYear(), calendar.fullCalendar("getDate").getMonth(), 1);
                                if ($.inArray(first_day, done_request) === -1) {
                                    render_event(first_date);
                                    done_request.push(first_day)
                                }
                            }
                        });
                    }
                };
                $.each(running_courses, function(i, v) {
                    pin_it.apply(this, ["green"]);
                });
                d(dates_arr);
                first_day_events();
                $.each(others_courses, function(i, v) {
                    pin_it.apply(this, ["red"]);
                })
                $.each(pending_courses, function(i, v) {
                    pin_it.apply(this, ["red"]);
                });
            });
        },
        clear_pins = function() {
            $("img.pin").remove();
        },
        clear_events = function() {
            $("div.user_sessions").remove();
            $("div.other_sessions").remove();
            $("div.single_sessions").remove();
            $("div.classroom").remove();
            $("div.date-header").remove();
            $("div.session").remove();
            $(".feedback-modal").remove();
            $(".attendance-modal").remove();
        };
    render_event = function(date) {
        if (render_event_done) {
            $.post("/get_centeroffering/", { "center_id": window.center_id, "day": date, "csrf_name": csrf_token }, function(resp) {
                clear_events();
                $("#calendar img.loader").remove();
                var curr_events = resp;
                var curr_event = null;
                render_event_done = true;
                var day_index = date.getDay();
                var day_mapping = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                var month_mapping = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                if (day_index == 7)
                    var day = day_mapping[0];
                else
                    var day = day_mapping[day_index];

                var month = month_mapping[date.getMonth()];

                $("#calendar").append("<div class='date-header'><p>" + day + ", " + month + " " + date.getDate() + "</p></div>");

                for (var index in curr_events) {
                    curr_event = curr_events[index]
                    students = curr_events[index].students;
                    window.curr_session_id = curr_event.id;
                    var that_index = index;
                    var topics = curr_event.topic;
                    var $topics_html = "";
                    for (var i in topics) {
                        var topic = topics[i];
                        if (topic.url != "")
                            $topics_html += "<a target='_blank' href='" + topic.url + "'>" + topic.title + " " + curr_event.grade + " " + curr_event.subject + "</a> ";
                        else
                            $topics_html += "<a href='#'>" + topic.title + ", " + curr_event.grade + " " + curr_event.subject + "</a> ";
                    }
                    var $html = "<div class='session'><div class='single_sessions user_session'><div style='float:left;'><p>" + curr_event.start + "</p></div><div style='margin-left:17px;float:left;margin-top:-3px;width:260px;'><p class='event-name'>" + $topics_html + "</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left;font-size:11px;'>" + "by <a class='teacher' href='#teacher-modal' data-toggle='modal' data-teacherid='" + curr_event.teacher_id + "'>" + curr_event.teacher + "</a> at <a class='center' href='#center-modal' data-toggle='modal' data-centerid='" + curr_event.center_id + "'>" + curr_event.center + "</a> <span class='session_status'> (" + curr_event.session_status + ")</span></p><div style='clear:both'></div></div></div></div>";

                    var $other_html = "<div class='session'><div class='single_sessions other_session'><div style='float:left;'><p>" + curr_event.start + "</p></div><div style='margin-left:17px;float:left;margin-top:-3px;width:260px;'><p class='event-name'>" + $topics_html + "</p><div style='clear:both'></div><p style='display:block;font-style:italic;margin-bottom:10px;float:left;font-size:11px;'>" + "by <a class='teacher' href='#teacher-modal' data-toggle='modal' data-teacherid='" + curr_event.teacher_id + "'>" + curr_event.teacher + "</a> at <a class='center' href='#center-modal' data-toggle='modal' data-centerid='" + curr_event.center_id + "'>" + curr_event.center + "</a> <span class='session_status'> (" + curr_event.session_status + ")</span></p><div style='clear:both'></div></div></div></div>";
                    var $feedback_modal = $('<div id="feedback-' + curr_session_id + '" class="feedback-modal modal hide" style=width:615px;"><img style="display:block;margin:10px auto" src="/static/images/loader.gif"/></div>');

                    var $attendance_modal = $('<div id="attendance-' + curr_session_id + '" class="attendance-modal modal hide" style=max-height:600px;"><img style="display:block;margin:10px auto" src="/static/images/loader.gif"/></div>');
                    if (curr_event.my_center === "Yes") {
                        $("#calendar").append($html).append($feedback_modal).append($attendance_modal);
                    } else if (curr_event.my_center === "No") {
                        $("#calendar").append($other_html)
                    }
                    (function(curr_session_id, $feedback_modal, $attendance_modal) {

                        $attendance_modal.on('show', function() {
                            if ($(this).children("img").length > 0) {
                                var $that = $(this);
                                $.get("/get_attendance?session=" + curr_session_id, function(resp) {
                                    $that.children("img").remove();
                                    $that.append(resp);
                                    $that.find("[rel='submit']").click(evd.ajax_submit);
                                });
                            }
                        });

                        $("#feedback-" + curr_session_id).on('show', function() {
                            if ($(this).children("img").length > 0) {
                                var $that = $(this);
                                $.get("/get_feedback?session=" + curr_session_id, function(resp) {
                                    event_render = true;
                                    $that.children("img").remove();
                                    $that.append(resp);
                                    $that.find("[rel='submit']").click(evd.ajax_submit);
                                });
                            }
                        });
                    }(curr_session_id, $feedback_modal, $attendance_modal));

                }
            }).error(function() {
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
            month: 'ddd', // Mon
            week: 'ddd d/M', // Mon 9/7
            day: 'dddd d/M' // Monday 9/7
        },
        eventSources: [{
            events: []
        }],
        eventMouseover: function(event, jsEvent, view) {
            if (view.name !== 'agendaDay') {
                $(jsEvent.target).attr('title', event.title);
            }
            return false;
        },
        eventRender: function(e, ele) {},
        dayClick: function(date, allDay, jsEvent, view) {
            clear_events();
            render_event(date);
            return false;
        }
    });
    var loaded_month = calendar.fullCalendar("getDate").getMonth() + 1,
        loaded_year = calendar.fullCalendar("getDate").getFullYear();
    render_events(loaded_month, loaded_year);
    $("td.fc-header-left > span.fc-button").click(function() {
        var loaded_month = calendar.fullCalendar("getDate").getMonth() + 1,
            loaded_year = calendar.fullCalendar("getDate").getFullYear();
        clear_pins();
        clear_events();
        render_events(loaded_month, loaded_year);
    });
    $("td.fc-header-right > span.fc-button").click(function() {
        var loaded_month = calendar.fullCalendar("getDate").getMonth() + 1,
            loaded_year = calendar.fullCalendar("getDate").getFullYear();
        clear_pins();
        clear_events();
        render_events(loaded_month, loaded_year);
    });

    $(".recommendations.modal").on("click", ".assign-btn", evd.ajax_submit);

    $(".assign-teacher").click(function() {
        var offering_id = $(this).attr("data-offering_id");
        $("#recomendations-" + offering_id).on("show", function() {
            if ($(this).children("img").length > 0) {
                var $that = $(this);
                $.get("/centeradmin_reco?offering_id=" + offering_id, function(resp) {
                    $that.children("img").remove();
                    $that.append(resp);
                    $that.find("form").append("<input type='hidden' value='" + window.center_id + "' name='center_id' />");
                })
            }
        });
    });

    $('.attendence-board > select').change(function() {

        var name = $(this).attr('name');
        var $board = $('.attendence-board')
        if (name === 'my_offerings') {
            var offering_Id = $(this).val(),
                options = $board.find('select[name="' + offering_Id + '"]').children('option').clone();
            $board.find("select[name='my_students']").empty().append(options);
            $board.children('.student_info').addClass('hide').find('tbody').html('');
        } else if (name === 'my_students') {
            var id = $(this).val();
            var temp = "<tr><td>${subject}</td><td>${present}/${total}</td><td>${absent}/${total}</td></tr>";
            if (id) {
                $.get("/attendance_mystudents/?id=" + id, function(resp) {
                    if (resp.length > 0)
                        $board.children('.student_info').addClass('hide').removeClass('hide').find('tbody').html('');
                    else
                        $board.children('.student_info').addClass('hide');
                    $.each(resp, function(i, obj) {
                        $board.children('.student_info').find('tbody').append('<tr></tr>');
                        $(temp).tmpl(obj).appendTo($board.children('.student_info').find('tbody > tr:last-child'));
                    });
                });
            } else {
                $board.children('.student_info').addClass('hide');
            }
        }
    });

    $(".mark_it_ascomplete").click(function(e) {
        var offering_id = $(this).attr('data-offering-id');
        message = 'Are you Sure \nOffering Id:' + offering_id + ' marked as complete and,\n';
        if (offering_id) {
            $.get("/complete_offering?offering_id=" + offering_id, function(resp) {
                if (resp.length > 0) {
                    for (let index = 0; index < resp.length; index++) {
                        const elment = resp[index];
                        message += '\n' + index + ' - ' + elment['id'] + ' - ' + elment['date'];
                    }
                    message += '\n\n**Delete these sessions in offering?';
                }

                console.log(message)
                var conf = confirm(message);
                if (conf) {
                    $.post("/complete_offering", {
                        offering_id: offering_id
                    }, function(resp) {
                        console.log(resp)
                        if (resp[0]['status'] == 'success') {
                            alert('Offering marked as complete and,\n feature sessions were deleted.');
                            location.reload();
                        }
                    });
                }

            }).fail(function(resp) {
                alert('Incomplete');
            });
        }
    });
    $("a[href='#add-session-modal']").click(function() {

        if ($(this).hasClass('add-sess')) {
            var start_date = $(this).data('start-date');
            var end_date = $(this).data('end-date');
            var offer = $(this).data('offering');
            var offer_nm = $(this).data('course_name');
            $('#add-sess-modal').find('#fromdt').val(start_date);
            $('#add-sess-modal').find('#todt').val(end_date);
            $('#add-sess-modal').find('#get_sess').data('offering', offer);
            $('#add-sess-modal').find('#course_nm').html(offer_nm);
        }

        $("#Completed-course-modal").find('.header > a').trigger('click');
        var offering_id = $(this).attr("data-offering");
        // hardcoded to indian offset
        if ($(this).attr("data-start-date") != "")
            var start_date = new Date(parseInt($(this).attr("data-start-date")) - 31800000);
        else
            var start_date = new Date();
        if ($(this).attr("data-end-date") != "")
            var end_date = new Date(parseInt($(this).attr("data-end-date")) - 31800000);
        else
            var end_date = new Date(start_date.getTime() + 3628800000);
    
        var $add_ses_modal = $("#add-session-modal");``
        $add_ses_modal.find("form").find("input[name='offering_id']").val(offering_id);
        $add_ses_modal.find("form").find("input.start_date_picker").val(start_date.getFullYear() + "-" + (start_date.getMonth() + 1) + "-" + start_date.getDate());
        $add_ses_modal.find("form").find("input.end_date_picker").val(end_date.getFullYear() + "-" + (end_date.getMonth() + 1) + "-" + end_date.getDate());
        var sday = ("0" + end_date.getDate()).slice(-2);
        var smonth = ("0" + (end_date.getMonth() + 1)).slice(-2);
        var eday = ("0" + end_date.getDate()).slice(-2);
        var emonth = ("0" + (end_date.getMonth() + 1)).slice(-2);
        var statdatestring = end_date.getFullYear()+"-"+(smonth)+"-"+(sday) ;
        var enddatestring = end_date.getFullYear()+"-"+(emonth)+"-"+(eday) ;
        document.getElementById("starts_date_id").value = ''+statdatestring;
        document.getElementById("ends_date_id").value = ''+enddatestring;
    });

    var new_session_count = 1;
    $("#add-new-button").click(function(e) {
        $(".tab-pane.active").removeClass("active");
        $(".evd.nav-tabs li.active").removeClass("active");
        var new_pane_id = "session-" + ++new_session_count;
        $new_tab_pane = $("#session-new").clone().attr({ "id": new_pane_id }).addClass("active"),
            $new_form = $new_tab_pane.find("form").attr({ "id": "form-" + new_pane_id }),
            $start_date = $new_form.find("input.start_date").removeClass("hasDatepicker");
        $end_date = $new_form.find("input.end_date").removeClass("hasDatepicker");
        $new_button = $new_form.find("a[rel=submit]").attr({ "id": "#form-" + new_pane_id });

        $('<li class="active"><a href="#' + new_pane_id + '" data-toggle="tab" pre-call="pre_add_session" callback="after_add_session">New Session (' + new_session_count + ')</a></li>').insertBefore($(this).parent("li"));
        $new_tab_pane.insertBefore($("#session-new"));
        $new_button.click(evd.ajax_submit);

        e.preventDefault();
    });

    $("li.dropdown, ul.dropdown-menu").mouseenter(function() {
        $(this).children("ul.dropdown-menu").show();
    });
    $("li.dropdown, ul.dropdown-menu").mouseleave(function() {
        $(this).children("ul.dropdown-menu").hide();
    });
    $("#ca-dashboard").on("click", "li.teacher", function() {
        var $preferences = $(this).children("div.preferences"),
            $expand = $(this).children("a.expand");
        if ($preferences.is(":hidden")) {
            $preferences.slideDown();
            $expand.text("-");
        } else {
            $preferences.slideUp();
            $expand.text("+");
        }
    });
    $("#ca-dashboard").on('click', ".assign-btn", function(e) {
        e.stopPropagation();
    });
    $("#teacher-1").show();
    $("select[name='user_id']").change(function() {
        var id = $(this).children(":selected").attr("data-teacher-id");
        $(".teachers").hide();
        $("#" + id).show();
    });

    $("#add-session-modal.modal").on("click", ".modify-btn", evd.ajax_submit);

    $(".add-session").click(function() {
        course_id = $(this).attr("data-run_course");
        var title = $(this).parents('li').children('span').text();
        $("#add-session-modal p.title span.title").text(title);

        if (course_id != undefined) {
            $("ul.nav-tabs li.current-session").addClass("active").show();
            $("ul.nav-tabs li.current-session").next("li").removeClass("active").hide();
            $("ul.nav-tabs li.current-session").next("li").children("a").text("Modify Sessions");
            $("#current_session").addClass("active").show();
            $("#session-1").removeClass("active");
            //       $("#add-session-modal").on("show", function(){
            var $current_session = $("#current_session");
            $.get("/current_sessions?offering_id=" + course_id, function(resp) {
                $current_session.children("img").remove();
                $current_session.children("div.modify-sessions").remove();
                $current_session.append(resp);
                //           })
            });
            $("#add-session-modal").on("hide", function() {
                var $current_session = $("#current_session");
                $current_session.children("img").remove();
                $current_session.children("div.modify-sessions").remove();
                $current_session.append('<img style="display:block;margin:10px auto" src="/static/images/loader.gif">');
            });
        } else {
            window.topics = $(this).attr("data-topics");
            $("ul.nav-tabs li.current-session").hide();
            $("ul.nav-tabs li.current-session").next("li").addClass("active").show();
            $("ul.nav-tabs li.current-session").next("li").children("a").text("Create Schedule");
            $("#current_session").removeClass("active");
            $("#session-1").addClass("active");
        }
    });

    if ($("#timings-table").parent("div").height() > 120) {
        $tr = $("#timings-table tbody tr:nth-child(4)").nextAll("tr");
        $("#timings-table tbody tr:nth-child(4)").nextAll("tr").hide();
        $("#timings-table").parent("div").append('<table id="timings"><tbody></tbody></table>');
        $("#timings").append($tr);
        $("#timings tr").show();
    }

    $("[rel=tooltip]").tooltip();
    $(".dashboard-calendar-container").on('change', '#status', function(e) {
        e.preventDefault();
        var stat = $(this).val(),
            res_code = $(this).parents('.drop-downs').next('.reason-code');
        if (stat === 'Cancelled' || stat === 'Rescheduled') {
            res_code.removeClass('hide');
        } else {
            res_code.addClass('hide');
        }
    });

    $("#calendar").on("click", ".teacher", function() {
        var teacher_id = Number($(this).attr("data-teacherid"));
        $.get("/get_teachers/?teacher_id=" + teacher_id, function(resp) {
            resp = eval(resp);
            var user_info = resp[0];
            if (user_info.short_notes == "")
                var title = "No notes is available";
            else
                var title = user_info.short_notes;
            var $user_block = "<div class='user-block' rel='tooltip' title='" + title + "' data-placement='left'>" +
                "<div>" +
                "<div style='overflow:hidden;'>" +
                "<form action='/save_remarks/' method='POST' id='remarks-form' style='padding-top:10px;' data-userid='" + user_info.id + "'>{% csrf_token %}" +
                "<div style='overflow:hidden;background:#E6E6FA'>" +
                "<img class='user-pic' src='" + user_info.picture + "' style='float:left;width:100px;height:100px'>" +
                "<div class='general-information'>" +
                "<p class='username'>" + user_info.name + "</p>" +
                "<p style='float:right'>" +
                "<select name='status' style='float:right'>" +
                "<option>" + user_info.status + "</option>" +
                "<option>New</option>" +
                "<option>Ready</option>" +
                "<option>Active</option>" +
                "<option>Dormat</option>" +
                "<option>Non-active</option>" +
                "</select>" +
                "</p>" +
                "<p style='clear:both;margin-top:0px;width:340px;'>" + user_info.role + "</p>" +
                "<p style='clear:both;width:130px;'><label>Medium: </label>" + user_info.medium + "</p>" +
                "<p style='width:210px;'><label>Location: </label>" + user_info.location + "</p>" +
                "<p><label>Avail From: </label>" + user_info.from + "</p>" +
                "<p style='margin-left: -19px;'><label>Avail To: </label>" + user_info.to + "</p>" +
                "</div>" +
                "</div>" +
                "</div>" +
                "<div style='width:467px;min-height:50px;font-size:small;padding:0px 10px;'>" +
                "<div class='info'>" +
                "<p class='email'><label>Email: </label>" + user_info.email + "</p>" +
                "<p class='phone'><label>Phone: </label>" + user_info.phone + "</p>" +
                "</div>" +
                "<p style='margin-top:5px;'><label>Current courses: </label>" + user_info.current_courses + "</p>" +
                "</div>" +
                "<div class='general_info preferences' style='width:467px !important'>" +
                "<p><label>Hours Contributed: </label>" + user_info.hrs_contributed + "</p>" +
                "<p style='float:left'><label>Remarks: </label></p>" +
                "<p style='float:left;padding-left:10px;'>" +
                "<input type='hidden' name='step' value=5 />" +
                "<input type='hidden' name='user_id' value='" + user_info.id + "' />" +
                "<textarea class='enabled' name='remarks' rows=2 cols=50 style='width:385px !important'>" + user_info.remarks + "</textarea>" +
                "</p>" +
                "<a class='btn hide' data-userid='" + user_info.id + "' rel='submit' callback='after_save' href='#remarks-form' style='cursor:pointer;width:50px;font-size:12px;float:right;line-height:18px;height:20px;margin-bottom:10px;'><span class='ajax-button-label' data-loading='wait'>Save</span></a>" +
                "</div>" +
                "</form>" +
                "</div>" +
                "<div class='preferences' style='padding:10px;float:left;width:440px;display:none'>" +
                "<p><label>Preferred Courses: </label></p>" +
                "<p>" + user_info.courses + "</p>" +
                "</div>" +
                "</div>" +
                "</div>";
            $("#teacher-modal img").hide();
            $("#teacher-modal").append($user_block);
            $(".user-block").on("click", ".btn", evd.ajax_submit);
        })
    });
    $("#teacher-modal").on("hide", function() {
        $("#teacher-modal .user-block").remove();
        $("#teacher-modal img").show();
    });
    var enabled = function() {
        $(this).find("a.btn").show();
    };
    $("#content").on("click", ".user-block", enabled);
    $("#html").not(".user-block").click(function() {
        $(".user-block a.btn").hide();
    });
    $("#content").on("mouseover", ".user-block", function() {
        $("[rel=tooltip]").tooltip();
    });

});


$("#fromdt").datepicker({
    defaultDate: "+1w",
    dateFormat: "dd-mm-yy",
    changeMonth: true,
    numberOfMonths: 3,
    /*onClose: function( selectedDate ) {
    $( "#todt" ).datepicker( "option", "minDate", selectedDate );
    }*/
});
$("#todt").datepicker({
    defaultDate: "+1w",
    dateFormat: "dd-mm-yy",
    changeMonth: true,
    numberOfMonths: 3,
    /*onClose: function( selectedDate ) {
    $( "#fromdt" ).datepicker( "option", "maxDate", selectedDate );
    }*/
});

$("#start_dt_off").datepicker({
    defaultDate: $('#todt').val(),
    dateFormat: "dd-mm-yy",
    changeMonth: true,
    numberOfMonths: 1,
});
$("#end_dt_off").datepicker({
    defaultDate: $('#fromdt').val(),
    dateFormat: "dd-mm-yy",
    changeMonth: true,
    numberOfMonths: 1,
});



$('.add-sess').click(function() {
    var start_date = $(this).data('start-date');
    var end_date = $(this).data('end-date');
    var offer = $(this).data('offering');
    var offer_nm = $(this).data('course_name');
    $('#add-sess-modal').find('#fromdt').val(start_date);
    $('#add-sess-modal').find('#todt').val(end_date);
    $('#add-sess-modal').find('#get_sess').attr('data-offering', offer);
    $('#add-sess-modal').find('#course_nm').html(offer_nm);
    $('#add-sess-modal').find('#start_dt_off').val(start_date);
    $('#add-sess-modal').find('#end_dt_off').val(end_date);
});

function updateOfferingsDate() {
    let confirm_off = confirm("Are you sure?");
    if (confirm_off) {
        var start_date = $('#start_dt_off').val();
        var end_date = $('#end_dt_off').val();
        var start_parts_date = start_date.split('-');
        var end_parts_date = end_date.split('-');
        // console.log(start_parts_date);
        var start_date_dt = new Date(start_parts_date[2], start_parts_date[1] - 1, start_parts_date[0]);
        var end_date_dt = new Date(end_parts_date[2], end_parts_date[1] - 1, end_parts_date[0]);
        // console.log(start_date_dt.toDateString());
        if (start_date_dt.getTime() < end_date_dt.getTime()) {
            var offer = $('#get_sess').attr("data-offering");
            var course_nm = $('#add-sess-modal').find('#course_nm').text();
            $.post('/v2/update_offerings_date/', { 'start_date': start_date, 'end_date': end_date, 'offer': offer, 'course_nm': course_nm }, function(resp) {
                alert(resp['msg']);
                course_nm = resp['course_name'];
            }).done(function() {
                getLoadClass(start_date, end_date);
                $('#add-sess-modal').find('#fromdt').val(start_date);
                $('#add-sess-modal').find('#todt').val(end_date);
                $('#add-sess-modal').find('#course_nm').text(course_nm);
            });
        } else {
            alert("Please select proper start and end date.")
        }
    }
}

function getLoadClass(from_date = $('#fromdt').val(), end_date = $('#todt').val()) {

    var offer = $('#get_sess').attr("data-offering");
    $('#load_modif').show();
    $.post('/get_ofr_sess/', { 'from_date': from_date, 'to_date': end_date, 'offer': offer }, function(resp) {
        resp5 = resp;
        var teacher_select = '<option value="">Select Teacher</option>';
        var topic_select = '';
        var offering = String(resp5.offering_id);
        _.each(resp5.users, function(usr) {
            teacher_select += '<option value=' + usr.id + '>' + usr.id + ' :: ' + usr.name + '</option>';
        });
        _.each(resp5.topics, function(topic) {
            topic_select += '<option value="' + topic.title + '" >' + topic.title + '(' + topic.num_sess + ')' + '</option>';
        });
        let count = 1;
        // console.log("RESPONSE", JSON.stringify(resp5.sessions));
        var modif_sess_tmpl = _.template("<%  _.forEach(resp5.sessions, function(u,i){  %>" +
            "<tr>" +
            "<td style='width:55px;' class='day_cls'><%=u.day%></td>" +
            "<td ><input style='width:100px;margin-bottom:0' type='text' class='input date-picker' value='<%=u.start_date%>' /></td>" +
            "<td><input type='text' class='times start_time prefered_timings_mor' style='margin-left:5%;' value='<%=u.start_time%>' /></td>" +
            "<td><input type='text' class='times end_time prefered_timings_eve' style='margin-left:5%;' value='<%=u.end_time%>' /></td>" +
            "<td><select class='planned-topics' id='planned-topics_<%= i %>' style='width:180px;margin-left:4%;'>" +
            "<option>Select Topic</option>" +

            "<%_.each(resp5.topics_list_sess,function(topic){%>" +
            "<option value='<%= topic.id%>' <% if(topic.title==u.planned_topic){%>selected='selected'<%} %> ><%=topic.title%></option>" +
            "<%})%>" +
            "</select></td>" +


            " <% if((u.teacher_id)){%>" +
            "<td><input type='text' class='searchAllTeachersId teacher modify_data' value='<%=u.teacher_id%> :: <%=u.teacher%>' placeholder='Select Teacher'   style='width:180px;margin-left:3%;margin-top:10%'> " +
            "</td>" +
            "<%}else{%>" +
            "<td><input type='text'  placeholder='Select Teacher' class='searchAllTeachersId teacher modify_data'   style='width:180px;margin-left:0%;margin-top:10%'> " +
            "</td>" +
            "<%}%>" +

            //  "<td><select class='softwareId' style='margin-left: -32%;'><option value='1'>webex</option></select></td>"+

            "<td><select class='softwareId''  style='width:85%;margin-left:-7%;'>" +

            "<option value = <%=u.software_id_selected[0]%> ><%=u.software_name[0]%></option>" +
            "<option value = <%=u.software_id_selected[1]%> ><%=u.software_name[1]%></option>" +
            "<option value = <%=u.software_id_selected[2]%> ><%=u.software_name[2]%></option>" +
            "<option value = <%=u.software_id_selected[3]%> ><%=u.software_name[3]%></option>" +
            "<option value = <%=u.software_id_selected[4]%> ><%=u.software_name[4]%></option>" +
            "</select></td>" +
            "<td><input type='text' value='<%=u.software_link%>' class='software_linkId' style='margin-bottom:0;width: 100%;margin-left:-3%;' class='software_link' /></td>" +
            "<td id='cell_<%= i %>'><% if(u.video_link == null || u.video_link == ''){%><button id='<%= i %>' value='' class='video_urls' onclick='openVideoModal(this.id)' style='padding:2px; font-size:13px;width:110%;background-color:#f15a22;border:#f15a22;border-radius:3px;margin-left:7%;'>Select Video</button><%} else {%><input onclick='openVideoModal(this.id)' class='video_urls' type='text' value='<%= u.video_link %>' style='width:110%; margin-left:3%; margin-top:30%;' name='video_url_selected' id='<%= i %>' readonly></td><%} %>" +
            "<td><select class='modes_' style='margin-right:-10%;'><option value='online' <% if(u.mode == 'online'){%>selected='selected' <% } %> >Online</option><option value='offline' <% if(u.mode == 'offline'){%>selected='selected' <% } %>>Offline</option></select></td>" +
            "<td><div class='btn  add-timing thisID' data-session='<%=u.session_id%>' style='cursor:pointer;'><span style='display:block;font-size:12px;'>-</span></div></td>" +
            "</tr>" +
            "    <% }) %>  ");
        $('.searchAllTeachersId').html(teacher_select);
        $('#extnd_topics').html(topic_select);
        $('#table_row').find('#modif-form-div').find('form').find('input[name="offering_id"]').val(offering);
        modif_sess_tmpl(resp5);
        $('#table_row').find('table').find('#exist_sess').html(modif_sess_tmpl);
        $('.times').timepicker({ 'step': 15, 'useSelect': true, 'timeFormat': 'H:i', 'minTime': '1:00am', 'maxTime': '00:59am' });
        $('.searchAllTeachersId').css('font-size', '15px')

        var autocomplete_data = {
            source: "/v2/ajax/get_allteachers?center_id=" + window.center_id,
            minLength: 1,
            autoFocus: true,
            select: function(event, ui) {
                $(this).val(ui.item.value);
            },
            change: function(event, ui) {
                if (ui.item) {

                    return;
                }
                //  else {
                // $(this).val('');}

            }

        }

        /* 
        function applyAutocomplete(teacherIDByName){
            alert(teacherIDByName)
            $(teacherIDByName).autocomplete(autocomplete_data)
        }*/

        $('.searchAllTeachersId').click(function() {

            $(this).autocomplete(autocomplete_data)
        });

        function applyAutocomplete(cloneCount) {

            $('#klon' + cloneCount).autocomplete(autocomplete_data);
        }

        var cloneCount = 0;
        var removed_sessions = "";
        var new_sessions = 0;
        var row_counter = $("#table_id").find("tr").length + 1;
        $('#table_row').find('form').find("input[name='new_sessions']").val(new_sessions);
        $("div.add-timing").click(function() {
            var $row1 = $(".thisID");
            //$row1 = $row1[1]; 

            $row1 = $($row1[0]).parents("tr");
            var $row = $(this).parents("tr");
            if ($(this).children("span").text() == "-") {
                $row.remove();
                removed_sessions += $(this).attr("data-session") + ";";
            } else {
                cloneCount = cloneCount + 1;
                $(this).children("span").text("+");
                var originaltopics = document.getElementsByClassName('planned-topics')[0].innerHTML;
                var softwareId_options = document.getElementsByClassName('softwareId')[0].innerHTML;
                var day_cls = $('.current_session_table tr:last').find('.day_cls').text();
                row_counter += 1;
                var trow = "<tr class='new-row'><td style='width:55px;' class='day_cls'>" + day_cls + "</td>" +
                    "<td ><input style='width:100px;margin-bottom:0' type='text' class='input date-picker' value='' /></td>" +
                    "<td><input type='text' class='times start_time prefered_timings_mor' value='' /></td>" +
                    "<td><input type='text' class='times end_time prefered_timings_eve' value='' /></td>" +
                    "<td><select id=\'planned-topics_" + row_counter + "\' class='planned-topics topicsCls' style='width:180px;margin-left:2%;'>" +
                    "</select></td>" +
                    "<td><input type='text' class='searchAllTeachersId teacher modify_data' value='' placeholder='Select Teacher'   style='width:180px;margin-left:-1%;margin-top:10%;'>" +
                    "<td><select class='softwareId' style='margin-left: -32%;'><option value='1'>Webex</option><option value='2'>Google Meet</option><option value='3'>Microsoft Teams</option><option value='4'>Skype</option><option value='5'>Zoom</option></select></td>" +
                    "<td><input type='text' value='' class='software_linkId' style='margin-bottom:0;width: 125%;margin-left:-30%;' class='software_link' /></td>" +
                    "<td id=\'cell_" + row_counter + "\'><button id=\'" + row_counter + "' value='' class='video_urls' onclick='openVideoModal(this.id)' style='padding:2px; font-size:13px;width:110%;background-color:#f15a22;border:#f15a22;border-radius:3px;margin-left:7%;'>Select Video</button></td>" +
                    "<td><select class='modes_' style='margin-right:-10%;'><option value='online' selected='selected'>Online</option><option value='offline'>Offline</option></select></td>" +
                    "<td><div onclick='redirect(this)' class='btn add-timing thisID' data-session='' style='cursor:pointer;'><span style='display:block;font-size:12px;'>-</span></div></td>" +
                    "</tr>"
                $row1.parents("#table_row").find('table').find('#exist_sess').append(trow);
                $('.times').timepicker({ 'step': 15, 'useSelect': true, 'timeFormat': 'H:i', 'minTime': '1:00am', 'maxTime': '00:59am' });
                $('.searchAllTeachersId').css('font-size', '15px')
                $(".topicsCls").html(originaltopics);



                applyAutocomplete(cloneCount);
                $('.new-row .searchAllTeachersId').click(function() {
                    $('.new-row .searchAllTeachersId').autocomplete(autocomplete_data)
                });

                $('.current_session_table tr:last').find('input.date-picker').attr("id", "").removeClass('hasDatepicker').removeData('datepicker').unbind().datepicker({ dateFormat: "dd-mm-yy", timeFormat: "hh:mm" });
                //$('.current_session_table tr:last').find('input.date-picker').attr("id", "")
                new_sessions = new_sessions + 1;
                /*var $clone = $row1.clone(true);
                   
                   var datepicker_id = Number($clone.find("input.date-picker").attr("id").split("dp")[1]) + 1;
                   $clone.find("input.date-picker").attr({"id": "dp"+datepicker_id});
                   $clone.addClass("new-row");
                   $clone.find("td .searchAllTeachersId").prop('id', 'klon' + cloneCount);
                   $clone.find("div.add-timing").children("span").text("-");
                   $clone.find("div.add-timing").attr({"data-session": ""});
                   $row1.parents("#table_row").find('table').find('#exist_sess').append($clone);
                   applyAutocomplete(cloneCount);
                   inc = inc+1;
                   $('.searchAllTeachersId'+inc).val('')
                   
                   $('.new-row .searchAllTeachersId').click(function(){
                       $('.new-row .searchAllTeachersId').autocomplete(autocomplete_data)
                   });
                  
                   $clone.find('input.date-picker').attr("id", "").removeClass('hasDatepicker').removeData('datepicker').unbind().datepicker({dateFormat: "dd-mm-yy", timeFormat: "hh:mm"});
                   new_sessions = new_sessions + 1;*/
            }

            $('#table_row').find('form').find("input[name='removed_sessions']").val(removed_sessions);
            $('#table_row').find('form').find("input[name='new_sessions']").val(new_sessions);
        });
        $(".date-picker").datepicker({
            dateFormat: "dd-mm-yy",
            timeFormat: "hh:mm"
        });


    }).done(function() {
        $('#load_modif').hide();
        $('#table_row,#dummy_submit_btn').show();
    });

}
$(function() { // let all dom elements are loaded
    $('#add-sess-modal').on('hide.bs.modal', function(e) {
        $('#fromdt,#todt').val('');
        $('.current_session_table').find('tbody').html('');
        $('#control-panel').hide().find('.panel-content').find('table').find('tbody').html('');
        $('#table_row,#submit-modify-sess,#dummy_submit_btn').hide();
    });
});

function redirect(that) {

    var $row = $(that).parents("tr");
    if ($(that).children("span").text() == "-") {
        $row.remove();
    }
}

function openVideoModal(id) {
    let offer_nm = $('#course_nm').text();
    let center_id = window.center_id
    let topics = $('#planned-topics_' + id).val()
    $.get('/v2/get_videos?center_id=' + center_id + '&offer_details=' + offer_nm + '&topics=' + topics, function(response) {
        modal_html = "<div class='row'>"
        if ('video_url' in response && response['video_url'].length > 0) {
            for (let index = 0; index < response['video_url'].length; index++) {
                modal_html += "<div class='col-md-4 col-sm-4 col-xs-4 col-lg-4'>"
                modal_html += "<input style='width: 5%;position: absolute;top:-50%;' type='radio' name='video_val' id='video_val_" + index + "\' name='video_val' value=\'" + response['video_url'][index] + "\'>"
                modal_html += "<a target='_blank' href=\'" + response['video_url'][index] + "\'><div style='position:absolute; z-index:500;height:100%;width:84%;margin-left:8%;'></div><iframe style='width: 95%;margin-left:8%;' src=\'" + response['video_url'][index] + "\'></iframe></a>"
                modal_html += "</div>"
                if (((index + 1) % 3) == 0) {
                    modal_html += "<br>"
                }
            }
        } else {
            modal_html += "<h3 style='text-align:center;'>Videos Not Available ...</h3></div>"
        }

        $('#video_modal').html(modal_html);
        let footer = "<button class='btn' id=\'select_video_id_" + id + "\' style='backgroud-color:#f15a22; color:#FFFFFF;' onclick='closeVideoModal(this.id)'>Select</button>"
        $('#video_modal_footer').html(footer);
        $("#videoModal").modal('show');
    })
}

function closeVideoModal(clicked_id) {
    selected_video_url = $("input[name='video_val']:checked").val();
    $("#videoModal").modal('hide');
    if (selected_video_url != undefined) {
        let id = clicked_id.split('_')
        id = id[id.length - 1]
            // $('#'+id).hide()
        cell_html = "<input onclick='openVideoModal(this.id)' class='video_urls' type='text' value=\'" + selected_video_url + "\' style='width:110%; margin-left:3%; margin-top:30%;' name='video_url_selected' id=\'" + id + "\' readonly>"
        $('#cell_' + id).html(cell_html);
    }
}

$('#add-sess-modal').find('#action_panel').click(function() {
    $('#control-panel').slideToggle('slow');
});
$('#add-sess-modal').find('#control-panel').find('.panel_btn').click(function() {
    $(this).css('background-color', '#34cc67').siblings().css('background-color', '#F15A22');
    var actn = $(this).data('id');
    if (actn == 'add') {
        $('#add-panel').css('display', 'flex').siblings('.panel-content').css('display', 'none');
    } else if (actn == 'delete') {
        $('#delete-panel').css('display', 'inline-block').siblings('.panel-content').css('display', 'none');
    }
});
$('#add_new_sess').click(function() {
    function chk_extent_times() {
        q = "";
        days = "";
        var valid = true;
        $.each($("#extnd_slots div.timing-inner-wrapper"), function(index, val) {
            var strt_time = $(this).children().eq(1).val();
            var end_time = $(this).children().eq(2).val();
            if (strt_time != 'From' && end_time != 'To') {
                strt_date = '01/01/2016 ' + $(this).children().eq(1).val();
                endd_date = '01/01/2016 ' + $(this).children().eq(2).val();
            } else {
                $(this).attr({ "rel": "tooltip", "data-title": "Please select preferred days", "data-placement": "left" }).tooltip("show");
                valid = valid && false;
                //  return ;
            }
            if ($(this).children().eq(1).val() != "From" && $(this).children().eq(2).val() != "To" && Date.parse(endd_date) > Date.parse(strt_date)) {
                q += $(this).children().eq(1).val() + "-" + $(this).children().eq(2).val() + (index < ($("#extnd_slots div.timing-inner-wrapper").length - 1) ? ";" : "");
                $("#extnd_slots input[name='prefered_timings']").val(q);
                days += $(this).children().eq(0).val() + (index < ($("#extnd_slots div.timing-inner-wrapper").length - 1) ? ";" : "");
                $("#extnd_slots input[name='prefered_days']").val(days);
            } else if (Date.parse(strt_date) >= Date.parse(endd_date)) {
                //evd.show_msg("End time cannot be less than start time");
                $(this).attr({ "rel": "tooltip", "data-title": "End time cannot be less than or equal to start time", "data-placement": "right" }).tooltip("show");
                valid = valid && false;
                //return ;
            } else if ($("#preferences").hasClass("active")) {
                //evd.show_msg("Invalid Preferred Days");
                $(this).attr({ "rel": "tooltip", "data-title": "Invalid prefered days", "data-placement": "left" }).tooltip("show");
                valid = valid && false;
                //return ;
            }
        });
        return valid;
    }

    function fields_valid() {
        var topics_list = $('#extnd_topics').val();
        var start_date = $('#extnd_start_date').val();
        var end_date = $('#extnd_end_date').val();
        var teacher = $('.searchAllTeachersId').val();
        var del_confirm = $('#del_confirm').is(':checked');
        var modify_software = $('#modify_session_software_platform').val();
        var modify_software_link = $('#modify_session_software_platform_link').val();
        if (topics_list != null && start_date != '' && end_date != '' && teacher != '') {
            return [true, [topics_list, start_date, end_date, teacher, del_confirm, modify_software, modify_software_link]];
        }
        return [false, []];
    }


    var times_valid = chk_extent_times();
    var fields_valid_res = fields_valid()
    if (times_valid == true && fields_valid_res[0] == true) {
        $('#load_modif').show();
        var pref_times = $("#extnd_slots input[name='prefered_timings']").val();
        var pref_days = $("#extnd_slots input[name='prefered_days']").val();
        var offer = $('#add-sess-modal').find('#get_sess').attr('data-offering');
        $.post('/reschedule_course/', {
                'user_id': fields_valid_res[1][3],
                'offering_id': offer,
                'start_date': fields_valid_res[1][1],
                'end_date': fields_valid_res[1][2],
                'topics': fields_valid_res[1][0],
                'prefered_days': pref_days,
                'prefered_timings': pref_times,
                'del_confirm': fields_valid_res[1][4],
                'software': fields_valid_res[1][5],
                'software_link': fields_valid_res[1][6]
            },
            function(resp) {
                evd.show_msg(resp);
                window.setTimeout('location.reload()', 500);
            }
        ).done(function() {
            $('#load_modif').hide();
            //$('#get_sess').trigger('click');
            $('#control-panel').slideToggle('slow');
            $('#extnd_start_date,#extnd_end_date,.searchAllTeachersId').val('');
            $('#extnd_topics').html('');
            getLoadClass();
        });
    } else {
        evd.show_msg('All Fields are required and also check the time slots');
    }
});