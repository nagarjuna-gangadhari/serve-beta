$(document).ready(function() {

    $('#popup').click(function() {

        var center = $('#sel_center').val();
        var offer = $('#sel_offers').val();
        var type = $('#sel_type').val();
        if (center != '' && offer != '' && type != '') {
            $(this).parent().attr('href', '#upload-modal');
            //  $('.panel').slideUp();
            // $('#bck').show();
            $('#upload-modal').modal('show');
            $('#upload-modal').modal('toggle');
        } else {
            disp_msg('Please select Center, Offering, Category to proceed..', 'red');
        }

    });

    $('#datepicker').datepicker({ maxDate: 0 });
    $('#sel_center').change(function() {
        var centers = $(this).val();
        var ay = $('#sel_ay').val();
        if (centers) {
            disp_msg('Please Wait...', 'green');
            let centers_data = JSON.stringify({
                'centers': centers,
                'ay': ay
            });

            $.ajax({
                url: "/get_offers/", // the endpoint
                type: "POST", // http method
                data: centers_data, // data sent with the post request
                dataType: "json",
                ContentType: 'application/json; charset=utf-8',

                success: function(response) {
                    console.log(response); // server response
                    var opts = '';
                    $.each(response, function() {
                        opts = opts.concat('<option value="' + this.id + '" >' + this.name + '</option>');
                    });
                    var blnk = '';
                    $('#sel_offers').html(blnk.concat(opts));
                    $('#msg_box').hide().find('p').text('').css('color', 'grey');

                },

                error: function(xhr, errmsg, err) {
                    disp_msg('An error occured. Please try again.', 'red');
                    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                }
            });
        }
    });
    $('#sel_type').change(function() {
        if ($(this).val() == '1') {
            //  $('.panel>select').css({'width':'150px'});
            $('#schol_type').show()
        } else {
            // $('.panel>select').css({ 'width': '200px' });
            $('#schol_type').hide();
        }




    });

    $('#get_temp').click(function() {
        var center = $('#sel_center').val();
        var offer = $('#sel_offers').val();
        var type = $('#sel_type').val();
        var scol_type = $('#schol_type').val();
        var version = $("select#version").find(":selected").val();
        console.log(scol_type);
        if (center != '' && offer != '' && type != '') {
            console.log(center, offer, type);
            $(this).parent().attr('href', '/get_temp/?center=' + center + '&offer=' + offer + '&type=' + type + '&scol_type=' + scol_type + '&version=' + version);
            $(this).parent().click();
        }
    });

    $('#up_file').change(function() {
        var pth = $(this).val();
        if (pth != '') {
            var temp = pth.split('.');
            if (temp[1] == 'xlsx' || temp[1] == 'xls') {
                $('#err_msg').hide();
            } else {
                $('#err_msg').text('Invalid File Format').show();
            }
        } else {
            $('#err_msg').text('Choose a file to upload').show();
        }
    });

    $('.uploadFlag').click(function() {
        //$(this).addClass('active');
        $("#uploadFlagId").val($(this).text());
        $("#upload").click();
    });
    $(".uploadFlagNo").click(function() {
        $("#upload-modal").modal('hide');
    });

    $('#upload').click(function() {
        var filee = $('#up_file').prop('files')[0];
        var offer = $('.panel').find('#sel_offers').val();
        var type = $('.panel').find('#sel_type').val();
        var assess_date = $('#datepicker').val();
        var version = $("select#version").find(":selected").val();
        var uploadFlag = $("#uploadFlagId").val();
        if (assess_date != '' && typeof filee != 'undefined') {
            formData = new FormData();
            formData.append('filee', filee);
            formData.append('offer', $('.panel').find('#sel_offers').val());
            formData.append('type', $('.panel').find('#sel_type').val());
            formData.append('asses_date', $('#datepicker').val());
            formData.append('version', version);
            formData.append('uploadFlag', uploadFlag);
            $('#err_msg').text('File Uploading. Please Wait...').show();
            $.ajax({
                type: "POST",
                url: '/process_excel/',
                data: formData,
                success: process_resp,
                processData: false,
                contentType: false
            });
            $('#msg_box1').hide().find('p').text('').css('color', 'grey');

        } else {
            $('#err_msg').text('Please Choose Assessment Date and File to proceed..').show();

        }
    });
    var prev_schol = '<table class="pure-table pure-table-striped">' +
        '<thead><tr><th>ID</th><th>Course ID</th><th>Course</th><th>Student</th><th>Category</th><th>Total Marks</th><th>Actual Marks</th><th>Is Present</th></tr></thead>' +
        '<%_.forEach(data1,function(u){%> ' +
        '<tr >' +
        '<td><%=u.id%></td><td><%=u.offer%></td><td><%=u.offer_name%></td><td><%=u.student%></td><td><%=u.category%></td><td><%=u.total%></td><td><%=u.actual%></td><td><%=u.is_present%></td>' +
        '</tr>' +
        '<%})%>' +
        '</table>';


    var prev_coschol = '<table class="pure-table pure-table-striped">' +
        '<thead><tr><th>ID</th><th>Course ID</th><th>Course</th><th>Student</th>' +
        '<th>Curious</th>' +
        '<th>Attentiveness</th>' +
        '<th>Self Confidence</th>' +
        '<th>Responsibility</th>' +
        '<th>Supportiveness</th>' +
        '<th>Initiativeness</th>' +
        '<th>Positive Attitude</th>' +
        '<th>Mannerism</th>' +
        '<th>Wider Perspective</th>' +
        '<th>Emotional Connect</th>' +
        '<th>Technology Exposure</th>' +
        '</tr><thead>' +
        '<%_.forEach(data1,function(u){%> ' +
        '<tr >' +
        '<td><%=u.id%></td><td><%=u.offer%></td><td><%=u.offer_name%></td><td><%=u.student%></td>' +
        '<td><%=u.curious%></td>' +
        '<td><%=u.attentiveness%></td>' +
        '<td><%=u.self_confidence%></td>' +
        '<td><%=u.responsibility%></td>' +
        '<td><%=u.supportiveness%></td>' +
        '<td><%=u.initiativeness%></td>' +
        '<td><%=u.positive_attitude%></td>' +
        '<td><%=u.mannerism%></td>' +
        '<td><%=u.wider_perspective%></td>' +
        '<td><%=u.emotional_connect%></td>' +
        '<td><%=u.technology_exposure%></td>' +
        '</tr>' +
        '<%})%>' +
        '</table>';
    var prev_diag = '<table class="pure-table pure-table-striped">' +
        '<thead><tr>' +
        '<%_.forEach(data1.hdr,function(u){%>' +
        '<th><%=u%></th>' +
        '<%})%>' +
        '</tr><thead>' +
        '<%_.forEach(data1.data,function(u,i){%> ' +
        '<tr >' +
        '<% _.forEach(u,function(uu,ii){%>' +
        '<td><%=uu%></td>' +
        '<%})%>' +
        '</tr>' +
        '<%})%>' +
        '</table>';



    var prev_temps = [prev_schol, prev_coschol, prev_diag];

    function process_resp(data) {
        if (data == 'File already present do you want to update the file') {
            $("#upload").hide();
            $(".uploadFlagDiv").show();
            $("#err_msg").css('margin-top', '-8%');
            $(".uploadFlagDiv").css('margin-bottom', '2%');
        }
        if (typeof data == 'object') {
            $('#err_msg').text('').hide();
            $('#upload-modal').modal('hide');
            console.log(typeof data);
            clr_msg();
            console.log(data);
            data1 = data.data;
            var templ = '';
            if (data.type == 'Scholastic') {
                templ = prev_temps[0];
            } else if (data.type == 'Coscholastic') {
                templ = prev_temps[1];
            } else if (data.type == 'Diagnostic') {
                templ = prev_temps[2];
                data1 = data;
            }
            preview_templ = _.template(templ);
            preview_templ(data1);
            $('#tbl').html(preview_templ).parent().slideDown();
            $('.panel,.instr').slideUp();
            $('#prv_sub').data('up_type', data.type).data('asses_date', data.asses_date).data('uploadFlag', data.uploadFlag);
            $('#tbl').find('table').data('resp', data1);
            window.setTimeout(footer_adjust(), 5000);
        } else if (typeof data == 'string') {
            $('#err_msg').text(data).show();
        }
    }

    $('#prv_sub').click(function() {
        var temp = $(this).siblings('#tbl').find('table').data('resp');
        var type = $(this).data('up_type');
        var asses_date = $(this).data('asses_date');
        var uploadFlag = $(this).data('uploadFlag');
        var version = $("select#version").find(":selected").val();
        if (type == 'Scholastic') {
            url = '/bulk_schol/';
            bulk_submit(url, temp, asses_date, uploadFlag);
            $('#reup').show();
            $(this).remove();
        } else if (type == 'Coscholastic') {
            url = '/bulk_coschol/';
            bulk_submit(url, temp, asses_date);
            $('#reup').show();
            $(this).remove();

        } else if (type == 'Diagnostic') {
            url = '/bulk_diag/';
            bulk_submit(url, temp, asses_date, uploadFlag, version);
            $('#reup').show();
            $(this).remove();
        }

    });

    var bulk_submit = function(url, data, asses_date, uploadFlag, version) {
            var version = version || 0;
            var up_data = JSON.stringify(data);
            $.post(url, { 'up_data': up_data, 'asses_date': asses_date, 'version': version, 'uploadFlag': uploadFlag }, function(resp) { disp_msg(resp, 'green') }).done(function() {});

        }
        //functions
    var disp_msg = function(msg, color) {

        $('#msg_box').show().find('p').text(msg).css('color', color);
    }
    var clr_msg = function() {

        $('#msg_box').hide().find('p').text('').css('color', 'grey');
    }


}); //end document ready