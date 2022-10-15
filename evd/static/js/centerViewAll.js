$(document).ready(function(){
refresh_data();
window.sr = ScrollReveal();
sr.reveal('.thumbnail');
}); //document ready end
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
        var sel_langs = [];
        var sel_loc = [];
        var filter_langs = $('#filter_langs').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_langs,function(u){
           sel_langs.push($(u).data('value'));
        });
        var filter_cont = $('#filter_location').find('.optns').find('div.checkbox').find('input:checked');
        _.forEach(filter_cont,function(u){
        	sel_loc.push($(u).data('value'));
        });
        return [sel_langs,sel_loc]
};
$(".fil_opts").click(function(){
    refresh_data();
});
function refresh_data()
    {
            var fil_data = get_filter_data();
            loading();
            var csrftoken = getCookie('csrftoken');
            var current_page = '';
            var next_page = '';
            var prev_page = ''
            var total_page = '';
            var pageId = $("#pageId").val();
            $.post('/v2/centers/',{'csrfmiddlewaretoken':csrftoken,'sel_langs':JSON.stringify(fil_data[0]),'sel_location':JSON.stringify(fil_data[1]),'page':pageId},function(resp){
            resp9=resp;
            current_page = resp.current;
            prev_page = resp.prev;
            next_page = resp.next;
            total_page = resp.total;
            var center_list_data = '';
            if (resp!=null && resp!='' && resp!='undefined'){
            	if (resp.center_data!=null && resp.center_data!='' && resp.center_data!='undefined'){
            		var jsonObjs = resp.center_data;
            		for(i=0;i<jsonObjs.length;i++){
            			/*alert(jsonObjs[0]['photo']);*/
            			center_list_data += '<div class="col-md-4 col-xs-4 mix">';
            			center_list_data += '<a class="already" href="/v2/centerDetails/?center_id='+jsonObjs[i]['id']+'" style="cursor: pointer; text-decoration: none">';
            			center_list_data += '<div class="thumbnail"><img class="thumb-img img-responsive" src="'+jsonObjs[i]['photo']+'" alt="No Image"/>';
            			center_list_data += '<div class="caption" style="background-color: white;height: 80px;"><h6> Name : '+jsonObjs[i]['name']+'</h6><h6> State : '+jsonObjs[i]['state']+'</h6>';
            			center_list_data += '</div></div></a></div>';
            		}
            	}
            }
            else{
            	center_list_data = 'No Data Available.';
            }
            if(resp9.center_data.length == 0){
                $('#thumbs_div').html('<p style="padding:10px;text-align:center;">No Data Matching Your filters..!</p>')
            }else{
                $('#thumbs_div').html(center_list_data);
            }
            var pagination_template = '';
            if(center_list_data!=null && center_list_data!=' ' && center_list_data!='undefined' && center_list_data.length>'0'){
            	pagination_template += "<ul class='pagination' style='padding:0px !important'>";
            	if(total_page > 1){
            		if(current_page >1){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+prev_page+")'"+prev_page+"' ><i class='fa fa-chevron-left'></i></a></li> ";
            		}else{
            			pagination_template += "<li><a class='page' href='javascript:void(0);'><i class='fa fa-chevron-left'></i></a></li> ";
            		}
            		if(current_page !=1){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination(1)'>1</a></li> ";
            		}
            		if(current_page > 4 && current_page <= 10){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-1)+")'"+(current_page-1)+"' >...</a></li> ";
            		}
            		if((current_page-50)>0){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-50)+")'"+(current_page-50)+"' >...</a></li> ";
            		}
            		if((current_page-11) > 0 && (current_page-11) != 1){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-11)+")'"+(current_page-11)+"' >"+(current_page-11)+"</a></li> ";
            		}
            		if((current_page-10)>0){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-10)+")'"+(current_page-10)+"' >...</a></li> ";
            		}
            		if((current_page-2) > 0 && (current_page-2) != 1){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-2)+")'"+(current_page-2)+"' >"+(current_page-2)+"</a></li> ";
            		}
            		if((current_page-1) > 0 && (current_page-1) != 1){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page-1)+")'"+(current_page-1)+"' >"+(current_page-1)+"</a></li> ";
            		}
            		pagination_template += "<li  class='active'><a class='page' href='javascript:void(0);' onclick='loadPagination("+current_page+")'"+current_page+"' >"+current_page+"</a></li> ";
            		if((current_page+1) <= total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+1)+")'"+(current_page+1)+"' >"+(current_page+1)+"</a></li> ";
            		}
            		if((current_page+2) <= total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+2)+")'"+(current_page+2)+"' >"+(current_page+2)+"</a></li> ";
            		}
            		if((current_page+10) < total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+10)+")'"+(current_page+10)+"' >...</a></li> ";
            		}
            		if((current_page+11) < total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+11)+")'"+(current_page+11)+"' >"+(current_page+11)+"</a></li> ";
            		}
            		if((current_page+50) < total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+50)+")'"+(current_page+50)+"' >...</a></li> ";
            		}
            		if((current_page >= (total_page-10)) && (current_page < (total_page-3))){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+(current_page+1)+")'"+(current_page+1)+"' >...</a></li> ";
            		}
            		if((current_page+3) <= total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+total_page+")'"+total_page+"' >"+total_page+"</a></li> ";
            		}
            		if(current_page < total_page){
            			pagination_template += "<li><a class='page' href='javascript:void(0);' onclick='loadPagination("+next_page+")'"+next_page+"' ><i class='fa fa-chevron-right'></i></a></li> ";
            		}else{
            			pagination_template += "<li><a class='page' href='javascript:void(0);'><i class='fa fa-chevron-right'></i></a></li> ";
            		}
            	}
            	pagination_template += "</ul>";
            }
            $('#pagination_data').html(pagination_template);
            window.sr = ScrollReveal();
            sr.reveal('.thumbnail');
            }).done(function(){
            });
    }
function loadPagination(Page){
	var pageId = $("#pageId").val(Page);
	refresh_data();
}