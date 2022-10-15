$(document).ready(function(){
window.pref_med= $(".med").attr("id");
window.pref_category= $("#prefcategoryId").val();
window.authenticatedId= $("#authenticatedId").val();
window.sel_category= $("#pref_categoryId").val();
window.sel_dueDate = '';
$(function(){
/*	var date_input = $('input[id="due_dateId"]');
	var container = $('.bootstrap-iso form').length > 0 ? $(
			'.bootstrap-iso form').parent() : "body";
	var options = {
		format : 'dd-mm-yyyy',
		container : container,
		todayHighlight : true,
		autoclose : true,
	};
	date_input.datepicker(options);	*/
 refresh_data();

});
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
        var over = '<div id="overlay">' +
            '<img id="loading" src="/static/images/loader_demand.gif" >' +
            '</div>';
        $(over).appendTo('#thumbs_div');

};



//get data from filters

var get_filter_data = function(){
	   var sel_days = [];
       var sel_cat = [];
//       sel_days = $("#due_dateId").val();
       sel_days = '';
       var filter_cat = $('#filter_category').find('.optns').find('div.checkbox').find('input:checked');
       _.forEach(filter_cat,function(u){
    	   sel_cat.push($(u).data('value'));
       });
       return [sel_dueDate,sel_cat]
};

$(".fil_opts").click(function(){
    refresh_data();
    $("#message_div").empty();
});

$("#due_dateId").change(function(){
	sel_dueDate = $("#due_dateId").val();
    refresh_data();
    $("#message_div").empty();
});

var refresh_data  =  function()
    {    
			/*window.sr = ScrollReveal();
			sr.reveal('.thumbnail');*/
            var fil_data = get_filter_data();
            loading();
            var csrftoken = getCookie('csrftoken');
            if( (fil_data[0]).length < 2 ){
                $('#demand_alert').removeClass('hide');
            }else{
                $('#demand_alert').addClass('hide');
            }
            $('#filter_days,#filter_times').tooltip('hide');
            $.post('/v2/demandListForOtherSkills/',{'csrfmiddlewaretoken':csrftoken,'sel_days':JSON.stringify(fil_data[0]),'pref_category':JSON.stringify(fil_data[1]),'sel_cats':window.sel_category},function(resp){
            resp9=resp;
            var demand_list_data = '';
            /*var colors = ['rgb(66, 173, 111)', '#df4a43', '#1799dd','#ea964c'];*/
            var colors = ['rgba(9, 87, 165, 0.8)', 'rgba(30, 148, 82, 0.9)',  'rgba(218,93,44,0.9)'];
            var j = 0;
            if (resp!=null && resp!='' && resp!='undefined'){
            	if (resp.data!=null && resp.data!='' && resp.data!='undefined'){
            		var jsonObjs = resp.data;
            		for(i=0;i<jsonObjs.length;i++){
            			demand_list_data += '<div class="col-md-4 col-xs-4 mix ';
            			if (resp.categories!=null && resp.categories!='' && resp.categories!='undefined'){
            				var categoryies = resp.categories;
            				var cat_data = categoryies.toString().split(",");
            				if (cat_data!=null && cat_data.length>0){
            					for(j=0;j<cat_data.length;j++){
            						if(jsonObjs[i]['category']==cat_data[j]){
            							demand_list_data += ' '+cat_data[j]+ '';
            						}
            					}
            				}
            			}
            			demand_list_data += '">';
            			if(jsonObjs[i]['category']== "MARKETING"){
            				demand_list_data += '<div class="thumbnail" ><div class = "heading_div" style="background-color:'+colors[j]+';"><h6 class="heading"><b>Marketing</b></h6></div></br>';
						}else if(jsonObjs[i]['category']== "ADMIN"){
							demand_list_data += '<div class="thumbnail" ><div class = "heading_div" style="background-color:'+colors[j]+';"><h6 class="heading"><b>Admin</b></h6></div></br>';
						}else if (jsonObjs[i]['category']== "IT"){
							demand_list_data += '<div class="thumbnail" ><div class = "heading_div" style="background-color:'+colors[j]+';"><h6 class="heading"><b>IT</h6></b></div></br>';
						}else if (jsonObjs[i]['category']== "REPORTING"){
							demand_list_data += '<div class="thumbnail" ><div class = "heading_div" style="background-color:'+colors[j]+';"><h6 class="heading"><b>Reporting</b></h6></div></br>';
						}else{
							demand_list_data += '<div class="thumbnail" ><div class = "heading_div" style="background-color:'+colors[j]+';"><h6 class="heading">'+jsonObjs[i]['category']+'</h6></div></br>';
						}
            			demand_list_data += '<div class="caption">';
            			if (jsonObjs[i]['subject']!=null && jsonObjs[i]['subject']!='' && jsonObjs[i]['subject']!='undefined'){
            				var subject = jsonObjs[i]['subject'];
            				subject = subject.replace("<", "&lt;");
    						subject = subject.replace(">", "&gt;");
          				  if(jsonObjs[i]['subject'].length>65){
          					  demand_list_data +='<p class="subject_styling" style="color:'+colors[j]+';">'+subject.substring(0,57)+'.<a href="javascript:void(0);" style="text-decoration:none;font-size:18px;color:'+colors[j]+';" onclick="toggleDataModelForSubject('+jsonObjs[i]['id']+');">...</a></p>';
                             }
                          else{
                          	 demand_list_data += '<p class="subject_styling" style="color:'+colors[j]+';">'+subject+'</p>';
                           	 }
            			}
            			 if (jsonObjs[i]['comment']!=null && jsonObjs[i]['comment']!='' && jsonObjs[i]['comment']!='undefined'){
            				 var comment = jsonObjs[i]['comment'];
            				 comment = comment.replace("<", "&lt;");
     						 comment = comment.replace(">", "&gt;");
            				  if(jsonObjs[i]['comment'].length>15){
                            	  demand_list_data += '<p style="padding-top: 15px;padding-bottom: 15px;height:60px;color:'+colors[j]+';">'+comment.substring(0,13)+'...<a href="javascript:void(0);" style="text-decoration:none;font-size:14px;color:#2EC7F0;" onclick="toggleDataModelForComment('+jsonObjs[i]['id']+');">Read more >></a></p>';
                               }
                               else{demand_list_data += '<p style="padding-top: 15px;padding-bottom: 15px;height:60px;color:'+colors[j]+';">'+comment+'</p>';}
            			 }
            			 else{
            				 demand_list_data += '<p style="padding-top: 15px;padding-bottom: 15px;height:60px;color:'+colors[j]+';">No comment available.</p>';
            			 }
            			 if(window.authenticatedId == "True"){
            				 demand_list_data += '<div style="text-align:center;margin-top: -10px;"><a class="btn btn-lg btn-primary scroll " onclick="updateOtherOpportunity('+jsonObjs[i]['id']+');" role="button" style=" cursor: pointer; text-decoration:none;font-size:14px;background-color: darkturquoise;">I Am Interested</a></div>';
            			 }
            			 else{
            				 demand_list_data += '<div style="text-align:center;margin-top: -10px;"><a class="btn btn-lg btn-primary scroll already"  data-toggle="modal" data-target="#login-modal" id="login-trigger2" style="cursor:pointer;text-decoration:none;background-color: darkturquoise;" onclick="addDataValue();">I Am Interested</a></div>';
            			 }
            			 demand_list_data += '<div style="text-align:center; margin-top:-10px;">';
            			 demand_list_data += '<input type="hidden" id="'+jsonObjs[i]['id']+'" value="'+jsonObjs[i]['comment']+'" data-sub="'+jsonObjs[i]['subject']+'"/></div>';
            			 demand_list_data += '</div></div></div>';		
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
            if(resp9.data.length == 0){
                $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Opportunity Matching Your filters..!</p>')
            }else{
                $('#thumbs_div').html(demand_list_data);
            }
            // window.sr = ScrollReveal();
            // sr.reveal('.thumbnail');
            }).done(function(){
            });
    }
//document ready end
