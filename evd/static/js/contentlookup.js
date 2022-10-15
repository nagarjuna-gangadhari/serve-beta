function getCookieValue(a) {
    var b = document.cookie.match('(^|[^;]+)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function book_video_classes_others(topic_id, workstream) {
    var topic_id = topic_id
    var teacher_id = "teacher_id" + String(topic_id)
    var user_id = document.getElementById(teacher_id).value
    console.log("id" + user_id)
    if (user_id == "") {
        alert("Please enter the Teacher id")

    } else {
        var post_data = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'teacher_id': user_id }
        $.post("/v2/verify_teacher/", post_data, function(resp) {
            if (resp.is_teacher == 0) {
                alert("Please enter valid Teacher id")

            } else {
                book_video_classes(topic_id, workstream, user_id)
            }

        })
    }

}

function book_video_classes(topic_id, workstream, teacher_id) {
    console.log("userdddd" + workstream, teacher_id)
    var post_data1 = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'topic_id': topic_id, 'workstream': workstream }
    $.post("/v2/topic_name/", post_data1, function(resp) {
        var post_data2 = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'topic_id': topic_id, 'workstream': workstream, 'teacher_id': teacher_id }
        $.post("/v2/verify_selected_topic/", post_data2, function(response) {

            var is_exists = response.is_exists
            var is_approved = response.is_approved
            var subtopic_status = response.subtopic_status
            console.log('sdccdsvdf', subtopic_status)
            if (response.subtopics_imcluded == 0) {
                alert(resp.topic_name + " doesnot contain any subtopic")
            } else if (is_approved == 1) {

                alert("You have already selected " + response.topic_name)
            } else if (is_exists == 0) {



                if (confirm('You have selected for ' + resp.topic_name)) {
                    // console.log("workstrem", document.getElementById("workstrem"))
                    var post_data3 = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'topic_id': topic_id, 'workstream': workstream, 'teacher_id': teacher_id }
                    $.post("/v2/book_video_classes/", post_data3, function(response) {
                        alert(response.message)
                        if (response.is_teacher == 1) {
                            window.location = "/myevidyaloka/"
                        } else {
                            window.location = "/v2/content_demand"
                        }


                    })
                }
            } else {
                console.log('subtopic_status', subtopic_status)
                if (subtopic_status == 0) {
                    if (confirm("Do u want to release previous topic - " + response.topic_name)) {
                        var post_data = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'topic_id': response.topic_id }
                        $.post("/v2/release_topic/", post_data, function(response) {
                            alert(response)
                            location.reload();

                        })
                    }
                } else {
                    if (confirm('You have selected for ' + resp.topic_name)) {
                        // console.log("workstrem", document.getElementById("workstrem"))
                        var post_data = { 'csrfmiddlewaretoken': getCookieValue('csrftoken'), 'topic_id': topic_id, 'workstream': workstream, 'teacher_id': user_id }
                        $.post("/v2/book_video_classes/", post_data, function(response) {
                            alert(response.message)
                            if (response.is_teacher == 1) {
                                window.location = "/myevidyaloka/"
                            } else {
                                window.location = "/v2/content_demand"
                            }


                        })
                    }

                }

            }

        })
    })
}
$(document).ready(function() {
    window.usr_status = $(".usr").attr("id");
    window.authenticatedId = $("#authenticatedId").val();
    window.pref_subject = $("#pref_subject_id").val();
    window.pref_grade = $("#pref_grade_id").val();
    window.pref_board = $("#pref_board_id").val();
    window.course_id = $("#course_id_id").val();
    $(function() {
        refresh_data();
    });

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

    function loading() {
        // add the overlay with loading image to the page
        var over = '<div id="overlay">' +
            '<img id="loading" src="/static/images/loader_demand.gif" >' +
            '</div>';
        $(over).appendTo('#thumbs_div');

    }

    function get_filter_data() {
        var sel_topics = [];
        var sel_workStream = [];
        var filter_topics = $('#filter_topics').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_topics, function(u) {
            sel_topics.push($(u).data('value'));
        });
        var filter_stream = $('#filter_workStream').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_stream, function(u) {
            sel_workStream.push($(u).data('value'));
        });
        return [sel_topics, sel_workStream]
    }

    //get data from filters
    $(".fil_opts").click(function() {
        refresh_data();
    });

    function refresh_data() {
        var fil_data = get_filter_data();
        loading();
        var csrftoken = getCookie('csrftoken');
        $.post('/v2/get_content_lookup/', { 'csrfmiddlewaretoken': csrftoken, 'sel_grades': pref_grade, 'sel_subjects': pref_subject, 'sel_boards': pref_board, 'topics': JSON.stringify(fil_data[0]), 'course_id': course_id, 'workStream': JSON.stringify(fil_data[1]) }, function(resp) {
            resp9 = resp;
            var demand_list_data = '';
            var colors = ['rgba(9, 87, 165, 0.8)', 'rgba(30, 148, 82, 0.9)', 'rgba(218,93,44,0.9)'];
            var j = 0;
            if (resp != null && resp != '' && resp != 'undefined') {
                var topic_details = resp.topic_details;
                if (topic_details != null && topic_details != '' && topic_details != 'undefined') {
                    for (i = 0; i < topic_details.length; i++) {
                        var topic_detail = topic_details[i];
                        demand_list_data += '<div class="col-md-4 col-xs-4 mix ';
                        //            			console.log(demand_list_data);
                        var my_grades = topic_detail['grades'];
                        if (my_grades.indexOf('5') > -1) { demand_list_data += '5 '; }
                        if (my_grades.indexOf('6') > -1) { demand_list_data += '6 '; }
                        if (my_grades.indexOf('7') > -1) { demand_list_data += '7 '; }
                        if (my_grades.indexOf('8') > -1) { demand_list_data += '8 '; }
                        if (my_grades.indexOf('9') > -1) { demand_list_data += '9 '; }
                        if (my_grades.indexOf('10') > -1) { demand_list_data += '10 '; }
                        if (my_grades.indexOf('11') > -1) { demand_list_data += '11 '; }
                        if (my_grades.indexOf('12') > -1) { demand_list_data += '12 '; }
                        demand_list_data += '">';
                        demand_list_data += '<div class="thumbnail" style="margin-top:20px;height:400px;padding: 0px ! important;border-radius: 5px !important;">';
                        demand_list_data += '<div class=" caption" style="background-color: ' + colors[j] + ';height: 80px; border-radius: 3px !important;border-bottom: 2px solid #e6e6e6;text-align: center;margin:1px auto ! important;" ><h6 style="font-size:25px;color:white;"><b>' + topic_detail['subject'] + '</b></h6></div>';
                        demand_list_data += '<div class="caption" style="height:170px;margin:10px;"><h6 style="color:' + colors[j] + ';" id="topic_id"><a href="#" data-toggle="tooltip"  title="'
                        for (l = 0; l < topic_details[i]['subtopic_list'].length; l++) {
                            demand_list_data += topic_details[i]['subtopic_list'][l]
                            demand_list_data += '\n'
                        }
                        demand_list_data += '"><b>Topic: ' + topic_detail['topic'] + '</b></h6></a><h6  style="color:' + colors[j] + ';">Work Stream: ' + topic_detail['workstream'] + '</h6></a>';
                        demand_list_data += '<h6 style="color:' + colors[j] + ';">Board: ' + topic_detail['board_name'] + '</h6><h6 style="color:' + colors[j] + ';">Grade: ';
                        var my_grades1 = topic_detail['grades'].toString();
                        var grade_list = my_grades1.split(",");
                        if (grade_list.length > 0) {
                            for (k = 0; k < grade_list.length; k++) {
                                demand_list_data += ' ' + grade_list[k] + 'th';
                                if (k != grade_list.length - 1) {
                                    demand_list_data += ',';
                                }
                            }
                        }


                        demand_list_data += '</h6><h6 style="color:' + colors[j] + ';">Videos Involved: ' + topic_details[i]['videos_involved']
                        demand_list_data += '</h6><h6 style="color:' + colors[j] + ';">Estimated Efforts: ' + topic_details[i]['videos_involved'] * 2 + 'hrs'
                        if (topic_details[i]['is_teacher'] == 0) {
                            demand_list_data += '<input type = "number" style = "width:150px;position: relative;top: 25px;left: 15px;" id ="teacher_id' + String(topic_details[i]['id']) + '">'
                        }
                        demand_list_data += '</h6></div>';
                        demand_list_data += '<div class="row thumb_row">'
                        demand_list_data += ' <div class="col-xs-12 col-sm-12 stat" style="position:relative;top:68px">';
                        if (authenticatedId == 'True') {
                            demand_list_data += '<a class="btn btn-lg btn-primary scroll already" href="javascript:void(0);"  style="cursor: pointer; text-decoration: none;background-color: darkturquoise;">';
                        } else {
                            demand_list_data += '<a class="btn btn-lg btn-primary scroll already" data-toggle="modal" data-target="#login-modal" id="login-trigger2" style="cursor:pointer;text-decoration:none;background-color: darkturquoise;" onclick="addDataValue();">'
                        }
                        if (topic_details[i]['is_teacher'] == 1) {
                            demand_list_data += '<span style="font-size:14px;color:blue;" onclick="book_video_classes(' + topic_details[i]['id'] + ',' + topic_details[i]['attribute_id'] + ',' + topic_details[i]['teacher_id'] + ')">Book</span></a></div></div></div></div>';
                        } else {
                            demand_list_data += '<span style="font-size:14px;color:blue;" onclick="book_video_classes_others(' + topic_details[i]['id'] + ',' + topic_details[i]['attribute_id'] + ')">Book for other</span></a></div></div></div></div>';
                        }
                        j++;
                        if (j > colors.length - 1) {
                            j = 0;
                        }
                    }

                } else {
                    demand_list_data = '<p style="padding:10px;text-align:center;">No Data Available...!</p>';
                }

            } else {
                demand_list_data = '<p style="padding:10px;text-align:center;">No Data Available...!</p>';
            }
            var subj_filter = _.template("<% _.forEach(resp9.unique_subjects,function(u){%>" +
                "<div class='checkbox'>" +
                " <label class='demand_label'>" +
                "<input type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_subject) {%> checked <%}%>><%=u%>" +
                "</label>" +
                "</div>" +
                "<% }) %>");
            var grade_filter = _.template("<% _.forEach(resp9.unique_grades,function(u){%>" +
                "<div class='checkbox'>" +
                " <label class='demand_label'>" +
                "<input type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_grade) {%> checked <%}%>><%=u%>" +
                "</label>" +
                "</div>" +
                "<% }) %>");
            var board_filter = _.template("<% _.forEach(resp9.unique_board,function(u){%>" +
                "<div class='checkbox'>" +
                " <label class='demand_label'>" +
                "<input type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_board) {%> checked <%}%>><%=u%>" +
                "</label>" +
                "</div>" +
                "<% }) %>");

            grade_filter(resp9.unique_grades);
            board_filter(resp9.unique_board);
            if (resp9.topic_details.length == 0) {
                $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Course Matching Your filters..!</p>')
            } else {
                $('#thumbs_div').html(demand_list_data);
            }

            $('#thumbs_div').html(demand_list_data);
            $('#sub_opts').html(subj_filter);
            $('#grade_opts').html(grade_filter);
            $('#board_opts').html(board_filter);
            //            subjectFilter();
            //            gradeFilter();
            //            boardFilter();
            window.sr = ScrollReveal();
            sr.reveal('.thumbnail');
            if (pref_subject != null && pref_subject != '' && pref_subject != 'undefined') {
                $("#sub_opts").trigger('click');
            }
            if (pref_grade != null && pref_grade != '' && pref_grade != 'undefined') {
                $("#grade_opts").trigger('click');
            }
            if (pref_board != null && pref_board != '' && pref_board != 'undefined') {
                $("#board_opts").trigger('click');
            }
        }).done(function() {

        });
    }

    // Subject filter 
    $("#sub_opts").on('click', '.fil_opts', function() {
        var checked_opts = $('#sub_opts').find('.fil_opts:checked');
        //getting month filter data
        var month_active_fil = $('#filters_div').find('button.fil_active');
        var month_fil_data = '';
        if (month_active_fil.length != 0) {
            month_fil_data = month_active_fil.data('filter');
        }
        if (checked_opts.length == 0) {
            $('.mix' + month_fil_data).fadeIn(500);
        } else {
            var un_checked = $('#sub_opts').find('.fil_opts').not(':checked');
            _.each(un_checked, function(u) {
                var sel_sub = $(u).data('value');
                $('.' + sel_sub).fadeOut(500);
            });
            _.each(checked_opts, function(u) {
                var sel_sub = $(u).data('value');
                $('.' + sel_sub + month_fil_data).fadeIn(500);
            });
        }

    });


    function gradeFilter() {
        var checked_opts = $('#grade_opts').find('.fil_opts:checked');
        //		console.log('gradefilter '+checked_opts.val());
        //getting subject filter data
        var checked_opts_sub = $('#sub_opts').find('.fil_opts:checked');
        var sub_fil_data = '';
        if (checked_opts_sub.length != 0) {
            _.each(checked_opts_sub, function(u) {
                sub_fil_data += $(u).data('value') + ' ';
            });
        }
        //getting month filter data
        var month_active_fil = $('#filters_div').find('button.fil_active');
        var month_fil_data = '';
        if (month_active_fil.length != 0) {
            month_fil_data = month_active_fil.data('filter');
        }
        if (checked_opts.length == 0) {
            $('.mix' + month_fil_data).fadeIn(500);
            $('.mix' + sub_fil_data).fadeIn(500);
        } else {
            var un_checked = $('#grade_opts').find('.fil_opts').not(':checked');
            _.each(un_checked, function(u) {
                var sel_grd = $(u).data('value');
                $('.' + sel_grd).fadeOut(500);
                //	                 console.log("sel_gradd not checked"+sel_grd);
            });
            _.each(checked_opts, function(u) {
                var sel_grd = $(u).data('value');
                $('.' + sub_fil_data + sel_grd + month_fil_data).fadeIn(500);
                //	                 console.log("checked"+sel_grd);
            });
        }
    }

    function boardFilter() {
        var checked_opts = $('#board_opts').find('.fil_opts:checked');
        //			console.log('board_opts '+checked_opts.val());
        //getting subject filter data
        var checked_opts_sub = $('#sub_opts').find('.fil_opts:checked');
        var sub_fil_data = '';
        if (checked_opts_sub.length != 0) {
            _.each(checked_opts_sub, function(u) {
                sub_fil_data += $(u).data('value') + ' ';
            });
        }

        //getting month filter data
        var month_active_fil = $('#filters_div').find('button.fil_active');
        var month_fil_data = '';
        if (month_active_fil.length != 0) {
            month_fil_data = month_active_fil.data('filter');
        }
        if (checked_opts.length == 0) {
            $('.mix' + month_fil_data).fadeIn(500);
            $('.mix' + sub_fil_data).fadeIn(500);
        } else {
            var un_checked = $('#board_opts').find('.fil_opts').not(':checked');
            _.each(un_checked, function(u) {
                var sel_grd = $(u).data('value');
                $('.' + sel_grd).fadeOut(500);
                //		                 console.log("sel_gradd not checked"+sel_grd);
            });
            _.each(checked_opts, function(u) {
                var sel_grd = $(u).data('value');
                $('.' + sub_fil_data + sel_grd + month_fil_data).fadeIn(500);
                //		                 console.log("checked"+sel_grd);
            });
        }
    }

    function loadPagination(page_number) {
        if (page_number != null && page_number != '' && page_number != 'undefined') {
            $("#page_data").val(page_number);
        } else {
            $("#page_data").val(0);
        }
        refresh_data();
    }

}); //document ready end