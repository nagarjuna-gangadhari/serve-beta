$(document).ready(function(){
	



   $.post('/v2/get_students_log_details/',{'center_id': parent.window.center_id,'status':'Alumni' }, function(resp){

	   

/*   var coscol_temp = "<div style='height:430px'>"+
                                    "<p style='font-size:14px;font-weight:bold;color:black;text-align:center;'>Events</p> "+
                                    "<div class='col-sm-8 cosch' style='overflow-y:auto;max-height:358px;'>       "+
                                    "<% _.forEach(resp2.data,function(u,i){ %> "+
                                    "<div class='details <% if(i==0){%>active<%}%> ' <% if(i!=0){ %> style='display:none'<%}%> data-id='<%=u.id%>' id='cosch_<%=u.id%>' >"+
                                    "<table class='table table-striped table-condensed'   > "+
                                    "<tr><th>Event Name</th><th>Event Description</th></tr>"+
                                    "<tbody>"+
                                    "<tr><td>Initiativeness</td><td class='edit'><%=u.lr_initiativeness%></td></tr>"+
                                    "</tbody>"+
                                    "</table>"+
                                    "</div>  "+
                                    "<%  }); %> "  +
                                    "</div>"+
                                    "</div>       ";

    var act_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:430px;;margin-bottom:10px;' > "+
                         "<div style='max-height:400px;height:360px;overflow-y:auto;'>"+
                         "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Story</p>"+
                         "          <table class='table table-striped table-hover'> "+
                         "               <th>Story Title</th><th>Achievement Description</th>"+
                         "               <% _.forEach(resp2.data, function(u){  %>  "+
                         "                   <tr data-id='<%=u.id%>'><td class='edit'><%= u.notes %></td><td class='edit inn'><%= u.grading %></td></tr> "+
                         "               <% }) %>  "+
                         "          </table> "+
                         " </div> "+
                         "          </div>       ";*/

 

  


  // Not required var form_array  = [schol_form,co_schol_form,act_form,uc_form,diag_form2];
//  var temp_array = [coscol_temp, act_temp];

   console.time('ConcatTimer');
   $('#student_details').hide();
   $('#loader').show();
   //processing response
         var ay_html    = "";
         var offer_html = "<option value='empty' data-ay='ay'>--- Select an Offer ---";
         var stud_html = "";
         resp1 =  resp;
         var t1 = _.template(" <%  _.forEach(resp1.offerings, function(u,i){  %> " +
                         "   <div class='offer_stud' id='offer_<%= u.offer_id%>' <% if(i!=0){ %> style='display:none;' <%}%> > "+
                         "   <% _.forEach(u.offer_en_stud, function(uu,i){  %>  "+
                         "    <div class='stud_details_block' id='stud_<%= uu.stud_id %>' <% if (i!=0){%> style='display:none;' <%}%> > "+
                         "      <div class='row hdr' >  "+
                         "          <div class='col-sm-2' style='padding-top:10px;' > "+
                         "             <img class='img-responsive img-thumbnail thumb'   src='/<%= uu.stud_photo %>'  />  "+
                         "          </div>  "+
                         "      <div class='col-sm-5' style='padding-top:10px;'>  "+
                         "             <label>Name :</label><p style='display:inline;padding-left:10px;'> <%= uu.stud_name %> </p><br> "+
                         "              <label>Grade :</label><p style='display:inline'> <%= uu.stud_grade %>  </p><br> "+
                         "              <label>Gender :</label><p style='display:inline'> <%= uu.stud_gender %></p><br> "+
                         "              <label>center :</label><p style='display:inline'> <%=uu.stud_center%></p><br> "+
                         "       </div> "+
                         "       <div class='col-sm-5' style='padding-top:10px;'> "+
                         "              <label>School RollNo :</label><p style='display:inline'> <%= uu.stud_sch_rollno %></p><br> "+
                         "              <label>eVidyaloka ID :</label><p style='display:inline;'> <%= uu.stud_id %></p><br> "+
                         "              <label>Father Occupation :</label><p style='display:inline;padding-left:10px;'> <%= uu.stud_fath_occ %></p><br> "+
                         "              <label>Mother Occupation :</label><p style='display:inline;'> <%= uu.stud_moth_occ %>  </p><br> "+
                         "       </div> "+
                         "       </div> "+
                         "      <div class='row sectns' style='padding-top:15px;margin-bottom:20px;font-size:13px;'> "+
                         "         <div class=' col-sm-12' > "+
                         "             <ul class='nav nav-tabs mystudent_nav' data-offer='<%= u.offer_id %>' data-id='<%= uu.stud_id %>' > "+
                         "                 <li role='presentation' class='active'><a  class='stud_att'  id='att_<%=uu.stud_id %>_<%=u.offer_id%>'>Academic Details</a></li> "+
                         "                 <li role='presentation'><a  class='stud_schol'  >Parental Status</a></li> "+
                         "                 <li role='presentation'><a  class='stud_coschol'  >Events</a></li> "+
                         "                 <li role='presentation'><a  class='stud_act'  >Story</a></li> "+
                         "             </ul> "+
                         "         </div> "+
                         "      </div> "+
                         "      <div class='row arena1 slides' style='display:none' >"+
                         "			<p style='text-align:center;font-weight:bold'>Parental Status</p>"+
                         " 			<div class='col-sm-offset-1 col-sm-10 col-sm-offset-1 lr_tables' style='overflow-y:auto;height:430px;margin-bottom:10px;'> "+
                         "				<table class='table table-striped table-hover'>"+
                         "              	<tr><th>Family Income</th><td><%= uu.stud_log_famliy_income %></td></tr>"+
                         "          	</table>"+
                         "			 </div>       "+
                         "      </div>"+
                         "      <div class='row arena2 slides'>"+
                         "			<p style='text-align:center;margin:20px 0px;font-weight:bold'>Academic Details</p>"+
                         "          <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:420px;;margin-bottom:10px;' id='lr_<%= uu.stud_id %>'>"+
                         "          <table class='table table-striped table-hover'>"+
                         "               <th>Current School</th><th>Current Grade</th><th>Notes on Performance</th>"+
                         "                   <tr><td><%= uu.stud_log_curr_schl %></td><td><%= uu.stud_log_curr_grade %></td><td><%= uu.stud_log_note_prfm %></td></tr>"+
                         "          </table>"+
                         "          </div>       "+
                         "      </div>"+
                         "      <div class='row arena3 slides'>"+
                         "			<p style='text-align:center;margin:20px 0px;font-weight:bold'>Story</p>"+
                         "          <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:420px;;margin-bottom:10px;' id='lr_<%= uu.stud_id %>'>"+
                         "          <table class='table table-striped table-hover'>"+
                         "               <th>Story Title</th><th>Achievement Description</th>"+
                         "               <% _.forEach(uu.stud_log_achivements, function(uuu){  %>  "+
                         "                   	<tr><td>Story Title</td><td><%= uuu %></tr>"+
                         "               <% }) %>  "+
                         "          </table>"+
                         "          </div>       "+
                         "      </div>"+
                         "      <div class='row arena5 slides'>"+
                         "			<p style='text-align:center;font-weight:bold'>Events</p>"+
                         " 			<div class='col-sm-offset-1 col-sm-10 col-sm-offset-1 lr_tables' style='overflow-y:auto;height:430px;margin-bottom:10px;'> "+
                         "				<table class='table table-striped table-hover'>"+
                         "              	<tr><th>Event Name</th><th>Event Description</th></tr>"+
                         "					<tr><td><%= uu.stud_log_event_name %></td><td><%= uu.stud_log_event_desc %></td></tr>"+
                         "          	</table>"+
                         "			 </div>       "+
                         "      </div>"+
                         "     </div> "+
                         "    <% }) %> </div>"+
                         "    <% }) %>  " );
       if(typeof resp1=='object'){
       t1( resp1.offerings );
        }else{
//         alert(resp1)
        }
       var offer_stud_html = "";
         resp.offerings.forEach(function(){
             var curr =  arguments[0];
             stud_html = "";
             offer_html += '<option value='+curr.offer_id+ ' data-ay=' + curr.offer_ay_id + ' >'+curr.offer_name+'</option> ';
             curr.offer_en_stud.forEach(function(){ 
                var curr1=arguments[0];
                stud_html += '<li class="list-group-item stud_ent" style="cursor:pointer;padding:4px 15px;" data-offer='+ curr.offer_id 
                             +' data-id='+ curr1.stud_id + ' data-ay_id=' + curr.offer_ay_id + ' > '+ curr1.stud_name +'</li>'  
             });
             offer_stud_html +='  <ul class="list-group stud_lists"  data-len="'+curr.offer_en_stud.length +'" id="students_list_'+curr.offer_id + '_' + curr.offer_ay_id +                                '"  style="display:none;max-height:460px;overflow-y:auto;"> '+ stud_html +' </ul> ';
         });
         //AY dropdown
         resp.ay_list.forEach(function(){
            var curr = arguments[0];
            ay_html += '<option value=' + curr.ay_id + '>' + curr.ay_title + ' ' + curr.ay_board + '</option>';
         });

  $('#student_details').html(t1);
   $('#sel_offer').html(offer_html);
   $('#sel_ay').html(ay_html);
   $('#sel_offer').change(function(){
         var ay_id = $('#sel_ay').val();
         var tmp="#students_list_"+$(this).val() + "_" + ay_id;  
         $('.stud_lists').hide();  
         var first = $(tmp).slideDown().find('.stud_ent').first();
         first.css({'background-color':'#F15A22', 'color':'white'});
         disp(first);
         $('#stud_badge').text($(tmp).data('len') || 0);
   });

   //$('#sel_ay option[value="' + resp1.current_ay + '"]').prop("selected", true);
   setTimeout(function(){$('#sel_ay').val(resp1.current_ay).trigger('change'), 0});
   //on change AY:
   $("body").on("change", "#sel_ay", function(){
      var ofr_id = $("#sel_offer").val();
      var ay_id = $(this).val();
      var offer_count = 0;
      var flag = true;
      $("#sel_offer > option").each(function() {
        if($(this).attr("data-ay") === ay_id){
            $(this).css("display", "block");
            if(flag){
                $(this).prop("selected", true);
                flag = false;
            }
            offer_count ++;
        } else if($(this).attr("data-ay") === 'ay'){
            $(this).prop("selected", true);
        } else{
            $(this).css("display", "none");
        }
      });
      $("#sel_offer").trigger("change");
      $("#off_badge").html(offer_count);

   });

   $('#off_badge').text(resp.offer_count);
   $('#students_list').html(stud_html);
   $('#students').html(offer_stud_html);
   $('#stud_badge').text($('.stud_lists').first().data('len'));
   setTimeout(function(){
    var disp = $("#sel_offer option:nth-child(2)").css("display");
    if(disp === "none"){
       $("#sel_offer").val("empty").trigger("change");
    }else{
       $("#sel_offer").val($("#sel_offer option:nth-child(2)").val()).trigger("change");
    }
   }, 0);
   //$("#sel_offer option:nth-child(2)").attr("selected",true);
   //$('#students').find('.stud_lists').first().show().find('.stud_ent').first().css({'background-color':'#F15A22', 'color':'white'});
   $(".mystudent_nav").find("li").find("a").css({'padding': '8px 12px', 'margin-right': '0'});
   $('#students').find('.stud_ent').click(function(){
         var ele = $(this);
         disp(ele);
   });
   // Caching responses

  

   function render_resp(resp, temp_dict, stud_id, offer_id){
      var stu_id = stud_id;
      var off_id = offer_id;
      var ky = stu_id+ '_' + off_id;
      if(_.has(temp_dict,ky)){
          temp = temp_dict.ky;
          return temp;
      }else{
          templt = _.template(     );

      }

   }


   //diagnostics form 
   //Diagnostics switch

   // Report Fetch
   $('a.stud_att').click(function(){ 
      disp_slide(this,'.arena2');
   });
   $('a.stud_coschol').click(function(){  
      //create_slide(this,temp_array[1]);
	   disp_slide(this,'.arena5');
   });
   $('.arena5,.arena1').on('click','.cositem',function(){
                $(this).siblings().removeClass('active');
                $(this).addClass('active');
                var ele = '#'+$(this).data('id');
                var ances = $(this).closest('.slides').find('.cosch');
                $(ances).children('.details').hide().removeClass('active');
                $(ances).children(ele).show().addClass('active');
   });


   $('a.stud_act').click(function(){
        //create_slide(this,temp_array[2]);
	   disp_slide(this,'.arena3');
   });
   $('a.stud_schol').click(function(){
      //create_slide(this,temp_array[0]);
	   disp_slide(this,'.arena1');
   });
   
   //displays  first particular element of student details block
   var disp = function(ele){
	   $("#log_type").empty();
         ele.parent().find('.stud_ent').css({'background-color':'', 'color':'black'});
         ele.css({'background-color':'#F15A22', 'color':'white'}).addClass("active_stud");
         var ofr = '#offer_'+ele.data('offer');
         var stu_id = '#stud_'+ele.data('id');
         var tab = get_curr_tab();
         $('.offer_stud').hide();
         $('.stud_details_block').removeClass('activ');
         $(ofr).slideDown().find('.stud_details_block').hide();
         $(ofr).find(stu_id).slideDown().addClass('activ').find('.sectns').find('a').filter('.'+tab).click();
         if (ele.length>0){
        	  $("#log_type").append('<h5 style="color:white;" >Log Type </h5><select class="form-control" style="margin-top:5px;width:100%;" id="log_type_id" onclick="triggerLog()"> '+
      				'<option value="1">Academic Details</option>'+
      				'<option value="2">Parental Status</option>'+
      				'<option value="3">Events</option>'+
      				'<option value="4">Story</option></select>');
        	  $("a.stud_att").trigger('click');
         }
   }

   //displays corresponding slide
   var disp_slide = function(block,slide){
       var ele1= $(block).parent('li');
       ele1.siblings().removeClass('active');
       ele1.addClass('active');
       var ele = $(block).closest('.sectns');
       ele.siblings('.slides').hide();
       ele.siblings(slide).show();

   }

var get_curr_tab = function(){
     var tab =  $('.stud_details_block').filter('.activ').find('.sectns').find('li.active').find('a').attr('class');
     console.log(tab);
     return tab;
}
//rendering
   var create_slide = function(that,templatee){
   var url = "";
   var target = "";
   if($(that).hasClass('stud_schol')){
      url ='/get_scholastic/';
      target =  '.arena1';
   }else if($(that).hasClass('stud_coschol')){
      url = '/get_co_schol/';
      target = '.arena5';
   }else if($(that).hasClass('stud_act')){
      url = '/get_activities/';
      target = '.arena3';
   }
   
      var temp = $(that).parent().parent();
      var stud_id = temp.data('id');
      var offer_id =  temp.data('offer');
      var kyy = stud_id+'_'+offer_id;
      $.post(url,{ 'stud_id':stud_id,'offer_id':offer_id,'csrfmiddlewaretoken':csrftoken },function(resp){
        resp2 = resp;
        var templ_c = _.template( templatee );
        templ_c(resp2.data);
        $(that).closest('.row').siblings(target).html(templ_c);
      });
      disp_slide($(that),target);


   }//end function
   }).done(function(){$('#student_details').show(); $('#loader').hide();});
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
var csrftoken = getCookie('csrftoken');

});// end document ready
