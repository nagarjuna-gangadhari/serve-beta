$(document).ready(function(){
window.pref_subject= $("#pref_subject_id").val();
window.usr_status= $(".usr").attr("id");
window.flag=$("#flag_id").val();
$('input[type=checkbox][data-value="'+pref_subject+'"]').prop('checked','checked');
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
// window.sr = ScrollReveal();
// sr.reveal('.thumbnail');


var loading = function() {
        // add the overlay with loading image to the page
        var over = '<div id="overlay">' +
            '<img id="loading" src="/static/images/loader_demand.gif" >' +
            '</div>';
        $(over).appendTo('#thumbs_div');

};

//get data from filters

function get_filter_data(){
	var sel_subjects = [];
    var filter_subjects = $('#filter_subjects').find('.optns').find('div.checkbox').find('input:checked');
    _.forEach(filter_subjects,function(u){
    	sel_subjects.push($(u).data('value'));
    });
    if (sel_subjects.length>0){
    	flag = false;
    }
    return [sel_subjects]
}
/*$(".fil_opts").click(function(){
    refresh_data();
});*/

$("#sub_opts").on('click','.fil_opts',function(){
	refresh_data();
});

$("#grade_opts").on('click','.fil_opts',function(){
	gradeFilter();
});

$("#board_opts").on('click','.fil_opts',function(){
	boardFilter();
});

var refresh_data  =  function()
    {
            var fil_data = get_filter_data();
            loading();
            var csrftoken = getCookie('csrftoken');
            $.post('/v2/get_content/',{'csrfmiddlewaretoken':csrftoken,'sel_subjects':JSON.stringify(fil_data[0]),'flag':flag},function(resp){
            resp9=resp;
            var demand_list_data = '';
            var colors = ['rgba(9, 87, 165, 0.8)', 'rgba(30, 148, 82, 0.9)',  'rgba(218,93,44,0.9)'];
            var j = 0;
            if (resp!=null && resp!='' && resp!='undefined'){
            	if (resp.data!=null && resp.data!='' && resp.data!='undefined'){
            		var jsonObjs = resp.data;
            		for(i=0;i<jsonObjs.length;i++){
            			demand_list_data += '<a class="already" href="/v2/content_lookup?course_id='+jsonObjs[i]['course_id']+'" style="cursor: pointer; text-decoration: none;">';
            			demand_list_data += '<div class="col-md-4 col-xs-4 mix ';
            			var my_grades = jsonObjs[i]['grades'].toString();
            			if (my_grades.indexOf('5')>-1){demand_list_data += '5 ';}
            			if (my_grades.indexOf('6')>-1){demand_list_data += '6 ';}
            			if (my_grades.indexOf('7')>-1){demand_list_data += '7 ';}
            			if (my_grades.indexOf('8')>-1){demand_list_data += '8 ';}
            			if (my_grades.indexOf('9')>-1){demand_list_data += '9 ';}
            			if (my_grades.indexOf('10')>-1){demand_list_data += '10 ';}
            			if (my_grades.indexOf('11')>-1){demand_list_data += '11 ';}
            			if (my_grades.indexOf('12')>-1){demand_list_data += '12 ';}
            			demand_list_data += ' '+jsonObjs[i]['board_name']+'">';
            			demand_list_data += '<div class="thumbnail" style="margin-top:20px;padding: 0px ! important;""><div class=" caption row thumb_row" style="background-color: '+colors[j]+';height: 80px; border-radius: 3px !important;border-bottom: 2px solid #e6e6e6;text-align: center;margin:1px auto ! important;" ><h6 style="font-size:25px;color:white;"><b>'+jsonObjs[i]['subject']+'</b></h6></div>';
            			demand_list_data += '<div class="caption" style="padding:20px !important;height: 180px;""><h6 style="color:'+colors[j]+';font-size:18px;">'+jsonObjs[i]['board_name']+'</h6>';
            			demand_list_data += '<h6 style="color:'+colors[j]+';font-size:18px;">Available For Grades: <br>';
            			var grades = jsonObjs[i]['grades'].toString();
            			var grade_list = grades.split(",");
            			if (grade_list.length>0){
                			for(k=0;k<grade_list.length;k++){
                				demand_list_data +=	' '+grade_list[k]+'th';
                				if (k!=grade_list.length-1){
                					demand_list_data += ',';
                				}
                			}
            			}
            			demand_list_data += '</h6>';
            			demand_list_data += '</div>';
            			demand_list_data += '</div></div></a>';
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
            var grade_filter = _.template("<% _.forEach(resp9.unique_grades,function(u){%>"+
                    "<div class='checkbox'>"+
                       " <label class='demand_label'>"+
                            "<input type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_grade) {%> checked <%}%>><%=u%>"+
                        "</label>"+
                    "</div>"+
                    "<% }) %>");
            var board_filter = _.template("<% _.forEach(resp9.unique_board,function(u){%>"+
                    "<div class='checkbox'>"+
                       " <label class='demand_label'>"+
                            "<input type='checkbox' data-value='<%=u%>' class='fil_opts' <% if (u == window.pref_board) {%> checked <%}%>><%=u%>"+
                        "</label>"+
                    "</div>"+
                    "<% }) %>");
            
            grade_filter(resp9.unique_grades);
            board_filter(resp9.unique_board);
            if(resp9.data.length == 0){
                $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Course Matching Your filters..!</p>')
            }else{
                $('#thumbs_div').html(demand_list_data);
            }
            $('#grade_opts').html(grade_filter);
            $('#board_opts').html(board_filter);
            gradeFilter();
            boardFilter();
            // window.sr = ScrollReveal();
            // sr.reveal('.thumbnail');
            if(pref_subject!=null && pref_subject!='' && pref_subject!='undefined'){
            	$("#sub_opts").trigger('click');
            }
           /* if(pref_grade!=null && pref_grade!='' && pref_grade!='undefined'){
            	$("#grade_opts").trigger('click');
            }*/
          /*  if(pref_board!=null && pref_board!='' && pref_board!='undefined'){
            	$("#board_opts").trigger('click');
            }*/
            
            }).done(function(){
            });
    }

function gradeFilter(){
	var checked_opts = $('#grade_opts').find('.fil_opts:checked');
	//getting board filter data
	var checked_opts_board = $('#board_opts').find('.fil_opts:checked');
	var board_fil_data='';
	 if(checked_opts_board.length!=0){
		 _.each(checked_opts_board,function(u){
			 board_fil_data += '.'+$(u).data('value');
    });
	    }
     if(checked_opts.length==0){
    	 console.log(checked_opts.length);
    	 if(board_fil_data.length != 0){
    		 _.each(checked_opts_board,function(u){
    			 var sel_board = '.'+$(u).data('value');
    			 $('.mix'+sel_board).fadeIn(500);
            });
    	 }else{
    		 $('.mix'+board_fil_data).fadeIn(500);
    	 }
        }else{
          var un_checked_grd = $('#grade_opts').find('.fil_opts').not(':checked');
          var un_checked_board = $('#board_opts').find('.fil_opts').not(':checked');
           _.each(un_checked_grd,function(u){
               var  sel_grd =  $(u).data('value');
               $('.'+sel_grd).fadeOut(500);
        });
          _.each(checked_opts,function(u){
              var  sel_grd =  $(u).data('value');
              var board_fil='';
              if(checked_opts_board.length !=0){
            	  _.each(checked_opts_board,function(m){
              		 if($(m).data('value')!= null & $(m).data('value') != '' & $(m).data('value')!='undefined'){
              			board_fil = '.'+$(m).data('value');
              			$('.'+sel_grd+board_fil).fadeIn(500);
              		 }
              	 });
              }else{
            	  $('.'+sel_grd).fadeIn(500);
              }
        });
        }
}
function boardFilter(){
		var checked_opts = $('#board_opts').find('.fil_opts:checked');
		//getting subject filter data
		var checked_opts_grade = $('#grade_opts').find('.fil_opts:checked');
		var grade_fil_data='';
		 if(checked_opts_grade.length!=0){
			 _.each(checked_opts_grade,function(u){
				 grade_fil_data +=  '.'+$(u).data('value');
	    });
		    }
	        if(checked_opts.length==0){
	        	if(grade_fil_data.length != 0){
	        		_.each(checked_opts_grade,function(u){
	   				 var sel_grade = '.'+$(u).data('value');
	   				 $('.mix'+sel_grade).fadeIn(500);
	   	           });
	        	}
	        	else{
	        		$('.mix'+grade_fil_data).fadeIn(500);
	        	}
	        }else{
	            var un_checked = $('#board_opts').find('.fil_opts').not(':checked');
	             _.each(un_checked,function(u){
	                 var  sel_board =  $(u).data('value');
	                 $('.'+sel_board).fadeOut(500);
	        });
	             _.each(checked_opts,function(u){
	                 var  sel_board =  $(u).data('value');
	                 var grade_fil='';
	                 if(checked_opts_grade.length !=0){
	                	 _.each(checked_opts_grade,function(m){
	 	             		 if($(m).data('value')!= null & $(m).data('value') != '' & $(m).data('value')!='undefined'){
	 	             			grade_fil = '.'+$(m).data('value');
	 	             			$('.'+sel_board+grade_fil).fadeIn(500);
	 	             		 }
	 	             	 });
	                 }else{
	                	 $('.'+sel_board).fadeIn(500);
	                 }
	             });
	        }
}
}); //document ready end