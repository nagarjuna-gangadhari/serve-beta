$(document).ready(function(){



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

    $('#up_file').change(function(){
        validate_file();
     });

      var validate_file = function(){
          var pth = $('#up_file').val();
          if(pth!=''){
              var temp = pth.split('.');
              if(temp[1]=='xlsx'||temp[1]=='xls'){
                    clr_msg();
                    return true;
              }
              else{
                    disp_msg('Invalid File Format','red');
                    return false;
              }
          }
          else{
                    disp_msg('Choose a file to upload','red');
                    return false;
          }
      }

      $('#upload').click(function(){
          var  filee = $('#up_file').prop('files')[0];
          var csrftoken = getCookie('csrftoken');
          if(typeof filee!='undefined' && validate_file()==true){
          formData = new FormData();
          formData.append('filee',$('input[type=file]')[0].files[0]);
          formData.append('csrfmiddlewaretoken', csrftoken);
          disp_msg('File Uploading. Please Wait...','green');
          $.ajax({
            type: "POST",
              url: '/bulk_usergen_xlrd/',
                data: formData,
                success: process_resp,
                  processData: false,
                  contentType: false
                    });
        }else{
             disp_msg('Please Choose a valid File to proceed..','red');

        }
      });
        var prev_users ='<table class="pure-table pure-table-striped">'+
                                 '<thead><tr><th>Email</th><th>Email 2</th><th>First Name</th><th>Last Name</th><th>Language</th><th>Phone</th><th>Duplicate/Invalid</th></tr></thead>'+
                                 '<%_.forEach(data1,function(u){%> '+
                                     '<tr <% if(u.duplicate=="Yes"){%> style="color:red;" class="discard"<% }%> >'+
                                     '<td><%=u.email_id%></td><td><%=u.email_id2%></td><td><%=u.first_name%></td><td><%=u.last_name%></td><td><%=u.language%></td><td><%=u.phone%></td><td><%=u.duplicate%></td>'+
                                     '</tr>'+
                                     '<%})%>'+
                                     '</table>';





     function process_resp(data){
          if(typeof data=='object'){
          console.log(typeof data);
          clr_msg();
          console.log(data);
          data1 = data.data;
          preview_templ = _.template(prev_users);
          preview_templ(data1);
          $('#tbl').html(preview_templ).parent().slideDown();
          $('.panel,.instr').slideUp();
          $('#tbl').find('table').data('resp',data1);
          $('#footer').css('position','relative');
          }else if(typeof data=='string'){
            disp_msg(data,'red');
            }
     }

    $('#prv_sub').click(function(){
              cdata=get_creation_data();
              url = '/bulk_user_create/';
              bulk_submit(url,cdata);
              $('#reup').show();
              $('#prv_sub,#prv_cancel').remove();
    });


var bulk_submit = function(url,data){
     var up_data = JSON.stringify(data);
     var csrftoken = getCookie('csrftoken');
     $.post(url,{'up_data':up_data,'csrfmiddlewaretoken': csrftoken},function(resp){ disp_msg(String(resp),'green')});
}
var get_creation_data = function(){
    var rows = $('#tbl').find('table').find('tbody').find('tr');
    var sub_data = [];
    _.each(rows,function(v,i){
            if($(v).hasClass('discard')==false){
                var tds = $(v).find('td');
                sub_data.push({'username':$(tds[0]).text(),'email':$(tds[0]).text(),'email2':$(tds[1]).text(),'first_name':$(tds[2]).text(),'last_name':$(tds[3]).text(),'language':$(tds[4]).text(),'phone':$(tds[5]).text()})
            }
    });
    return sub_data;
}
//functions
var disp_msg = function(msg,color){
    $('#msg_box').show().find('p').text(msg).css('color',color);
    }
var clr_msg = function(){
    $('#msg_box').hide().find('p').text('').css('color','grey');
    }


});//end document ready


