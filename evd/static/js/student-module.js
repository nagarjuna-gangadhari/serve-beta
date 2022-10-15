$(document).ready(function() {



    $.post('/get_off_stud/', { 'center_id': parent.window.center_id, 'ay_id': parent.window.ay_id }, function(resp) {

        tab_id = $("#hidden_tab_id").val();
        console.log('tab_id ', resp)


        var coscol_temp = "<div style='height:430px'>" +
            " <div class='col-sm-4 cosch_list' >  " +
            " <div class='list-group'> " +
            " <a  class='list-group-item disabled ' style='padding:4px;margin-top:29px;text-align:center'>Available Records</a>" +
            " <% _.forEach(resp2.data, function(u,i){ %>" +
            " <a  class='list-group-item cositem <% if(i==0){%>active<%}%>' data-id='cosch_<%=u.id%>' style='cursor:pointer;padding:0px 15px;'>By: <%=u.assessed_by%> On: <%=u.date%></a>" +
            "<%  }); %> " +
            "</div>       " +
            "</div>       " +
            "<p style='font-size:14px;font-weight:bold;color:black;text-align:center;'>Co-Scholastic Details</p> " +
            "<div class='col-sm-8 cosch' style='overflow-y:auto;max-height:358px;'>       " +
            "<% _.forEach(resp2.data,function(u,i){ %> " +
            "<div class='details <% if(i==0){%>active<%}%> ' <% if(i!=0){ %> style='display:none'<%}%> data-id='<%=u.id%>' id='cosch_<%=u.id%>' >" +
            "<table class='table table-striped table-condensed'   > " +
            "<tr><th>Parameter</th><th>Rating</th></tr>" +
            "<tbody>" +
            "<tr><td>Initiativeness</td><td class='edit'><%=u.lr_initiativeness%></td></tr>" +
            "<tr><td>Responsibility</td><td class='edit'><%=u.lr_responsibility%></td></tr>" +
            "<tr><td>Supportiveness</td><td class='edit'><%=u.lr_supportiveness%></td></tr>" +
            "<tr><td>Attentiveness</td><td class='edit'><%=u.pr_attentiveness%></td></tr>" +
            "<tr><td>Curious</td><td class='edit'><%=u.pr_curious%></td></tr>" +
            "<tr><td>Self confidence</td><td class='edit'><%=u.pr_self_confidence%></td></tr>" +
            "<tr><td>Emotional Connect</td><td class='edit'><%=u.ee_emotional_connect%></td></tr>" +
            "<tr><td>Technology Exposure</td><td class='edit'><%=u.ee_technology_exposure%></td></tr>" +
            "<tr><td>Wider Perspective</td><td class='edit'><%=u.ee_widerperspective%></td></tr>" +
            "<tr><td>Courteousness</td><td class='edit'><%=u.bh_courteousness%></td></tr>" +
            "<tr><td>Positive Attitude</td><td class='edit'><%=u.bh_positive_attitude%></td></tr>" +
            "</tbody>" +
            "</table>" +
            "</div>  " +
            "<%  }); %> " +
            "</div>" +
            "<div class='row' style='bottom:100px;;position:absolute;width:96%;margin-left:25px;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_cosch' style='width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_cosch' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_cosch' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_co_sch'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "</div>       ";
        var report_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:hidden;height:430px;;margin-bottom:10px;' > " +
            "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Progress Reports</p>" +
            "<div style='max-height:350px;height:330px;overflow-y:auto;'>" +
            "          <table class='table table-striped table-hover' style='max-height:300px;'> " +
            "               <th>Generation Date</th><th>Download Link</th> " +
            "               <% _.forEach(resp2.data, function(u){  %>  " +
            "                   <tr ><td><%= u.gen_date%></td><td><a href='<%= u.link %>'>Download</a></td><td><%= u.date %></td></tr> " +
            "               <% }) %>  " +
            "          </table> " +
            " </div> " +
            "          </div>       ";
        var act_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:390px;;margin-bottom:10px;' > " +
            "<div style='max-height:400px;height:360px;overflow-y:auto;'>" +
            "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Activity Details</p>" +
            "          <table class='table table-striped table-hover'> " +
            "               <th>Notes</th><th>Grading</th><th>Assesed By</th><th>Date</th> " +
            "               <% _.forEach(resp2.data, function(u){  %>  " +
            "                   <tr data-id='<%=u.id%>'><td class='edit'><%= u.notes %></td><td class='edit inn'><%= u.grading %></td><td><%= u.assessed_by %></td><td><%= u.date %></td></tr> " +
            "               <% }) %>  " +
            "          </table> " +
            " </div> " +
            "<div class='row' style='bottom:0;position:absolute;width:96%;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_act' style='width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_act' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_act' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_act'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "          </div>       ";

        var uc_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:390px;;margin-bottom:10px;' > " +
            "<div style='max-height:400px;height:360px;overflow-y:auto;'>" +
            "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Unique Characterstic Details</p>" +
            "          <table class='table table-striped table-hover'> " +
            "               <th>Strength</th><th>Weakness</th><th>Assesed By</th><th>Date</th> " +
            "               <% _.forEach(resp2.data, function(u){  %>  " +
            "                   <tr data-id='<%=u.id%>' ><td class='edit' style='width:150px;'><%= u.strengths %></td><td style='width:150px;' class='edit'><%= u.weaknesses %></td><td><%= u.assessed_by %></td><td><%= u.date %></td></tr> " +
            "               <% }) %>  " +
            "          </table> " +
            "<div class='row' style='bottom:0;position:absolute;width:96%;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_uc' style='width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_uc' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_uc' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_uc'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "</div>" +
            " </div>       ";
        var scol_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1 lr_tables' style='overflow-y:auto;height:390px;margin-bottom:10px;'> " +
            "<div style='max-height:400px;height:380px;overflow-y:auto;'>" +
            "<div class='subject_list'>" +
            "<p style='display:inline;margin:10px;'>Scores in other subjects :</p>" +
            "<% _.forEach(resp2.data,function(u,i){ %>" +
            "<button class='btn btn-success btn-xs cositem <%if(i==u.sel_offer){%>active<%}%>' data-id='schol_<%=u.offer%>' style='display:inline-block;width:auto;margin:10px;'><%=u.sub%>   </button>" +
            "<%})%> " +
            "</div>" +
            "<br>" +
            "<p style='text-align:center;font-weight:bold'>Scholastic Details</p>" +
            "<div class='cosch ' style='max-height:280px;overflow-y:auto;' >" +
            "<% _.forEach(resp2.data,function(u,i){  %>" +
            "<table class='table table-striped table-hover details <%if(i==u.sel_offer){%>active<%}%> ' id='schol_<%=u.offer%>' style='<% if(i!=u.sel_offer){%>display:none <% }%>'>" +
            " <tr><th>Subject</th><th>Category</th><th>Total</th><th>Actual</th><th>Assessed By</th><th>Is Present</th><th>Date</th></tr> " +
            "<% _.forEach(u.details, function(uu){ %> <tr data-id='<%=uu.id%>'> <td> <%= uu.subject %> </td><td><%=uu.category%></td><td class='edit'> <%= uu.total %> </td><td class='edit' > <%= uu.actual  %>  </td><td> <%= uu.assessed_by %> </td><td><%= uu.is_present %></td><td> <%= uu.date  %> </td></tr> <%  }); %> " +
            "</table>" +
            "<%})%>" +
            "</div>" +
            "</div>" +
            "<div class='row' style='bottom:0;position:absolute;width:96%;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_sch' style='<%if(!resp2.data){%>display:none;<%}%>width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_sch' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_sch' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_sch'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "</div>";
        var schol_lfh_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1 lr_tables' style='overflow-y:auto;height:390px;margin-bottom:10px;'> " +
            "<div style='max-height:400px;height:380px;overflow-y:auto;'>" +
            "<div class='subject_list'>" +
            "<p style='display:inline;margin:10px;'>Scores in other subjects :</p>" +
            "<% _.forEach(resp2.data,function(u,i){ %>" +
            "<% if(i != 'all_topics'){%>" +
            "<button class='btn btn-success btn-xs cositem active' data-id='schol_<%=u[0].offer_id%>' style='display:inline-block;width:auto;margin:10px;'><%=i%></button>" +
            "<%}%>" +
            "<%})%> " +
            "</div>" +
            "<br>" +
            "<p style='text-align:center;font-weight:bold'>Scholastic LFH Details</p>" +
            "<div class='cosch ' style='max-height:280px;overflow-y:auto;' >" +
            "<% _.forEach(resp2.data,function(u,i){  %>" +
            "<table class='table table-striped table-hover details active' id='schol_<%=u[0].offer_id%>'>" +
            "<% if(Object.keys(resp2.data).length == 1){ %>" +
            "</br></br><p style='font-weight:bold; text-align:center;'>No Data Available. Please add scholatic-lfh data</p>" +
            "<% } %>" +
            "<% if(i != 'all_topics'){%>" +
            " <tr><th>Subject</th><th>Topics</th><th>Outcome</th><th>Is Present</th><th>Type</th><th>Date</th>" +
            "<% _.forEach(u, function(uu){ %> <tr data-id='<%=uu.lfh_id%>'> <td> <%= uu.subject %> </td><td><%=uu.topic%></td><td id='outcome' class='edit'> <%= uu.outcome %> </td><td id='is_present' class='edit' > <%= uu.is_present  %>  </td><td id='record_typ' class='edit'> <%= uu.record_type %> </td><td id='record_dt' class='edit'> <%= uu.record_date %> </td></tr> <%  }); %> " +

            "</table>" +
            "<%}%><%})%>" +
            "</div>" +
            "</div>" +
            "<div class='row' style='bottom:0;position:absolute;width:96%;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_sch_lfh' style='<%if(!resp2.data){%>display:none;<%}%>width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_sch_lfh' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_sch_lfh' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_sch_lfh'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "</div>";

        var diag_temp = "<div style='height:430px'>" +
            " <div class='col-sm-4 cosch_list' >  " +
            " <div class='list-group'> " +
            " <a  class='list-group-item disabled ' style='padding:4px;margin-top:29px;text-align:center'>Available Records</a>" +
            " <% _.forEach(resp2.data, function(u,i){ %>" +
            " <a  class='list-group-item cositem <% if(i==0){%>active<%}%>' data-id='diag_<%=u.id%>' style='cursor:pointer;padding:0px 15px;;'>Sub : <%=u.subject%> On: <%= u.date_created %></a>" +
            "<%  }); %> " +
            "</div>       " +
            "</div>       " +
            "<p style='font-size:14px;font-weight:bold;color:black;text-align:center;'>Diagnostic Details</p> " +
            "<div class='col-sm-8 cosch' style='overflow-y:auto;max-height:360px;'>       " +
            " <% _.forEach(resp2.data, function(u,i){ %>" +
            "<div  class='details <% if(i==0){%>active<%}%> ' <% if(i!=0){ %> style='display:none'<%}%> id='diag_<%=u.id%>' >" +
            "<p style='float:left;font-size:13px;font-weight:bold;'>Level Scored : <span style='color:green'><%=u.aggregate_level%></p>" +
            "<table class='table table-striped table-condensed '   > " +
            "<tr><th>Parameter</th><th>Level</th><th>Total</th><th>Actual</th></tr>" +
            "<tbody>" +
            "<% _.forEach(u.details,function(uu,i){ %> " +
            "<tr data-id='<%=uu.id%>'  ><td ><%= uu.param_name %></td><td><%= uu.param_level %> </td><td><%= uu.total_marks %></td><td class='edit'><%= uu.actual_marks%></td></tr>" +
            "<%  }); %> " +
            "</tbody>" +
            "</table>" +
            "</div>" +
            "<%  }); %> " +
            "</div>  " +
            "<div class='row' style='bottom:100px;;position:absolute;width:96%;margin-left:15px;'> " +
            "<button type='button' class='btn btn-primary btn-sm editor_diag' style='width:100px;'><i class='glyphicon glyphicon-edit'></i>&nbsp&nbspEdit</button>" +
            "<button type='button' class='btn btn-danger btn-sm cancel_diag' style='display:none;width:100px;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "<button type='button' class='btn btn-success btn-sm update_diag' style='margin-left:10px;display:none;width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspUpdate</button>" +
            "<button type='button' style='float:right;background-color:#F15A22;' class='btn btn-warning btn-sm add_diag'><i class='glyphicon glyphicon-plus'></i>&nbsp&nbspAdd New</button>" +
            " </div> " +
            "</div>       ";

        var schol_form = "<form>" +
            "<h5 style='font-weight:bold;text-align:center;margin-bottom:10px;'>Scholastic Form<h5>" +
            "<p style='color:red;text-align:center;display:none' class='err_msg' >Please enter Required Fields...</p>" +
            "<div class='col-sm-offset-3 col-sm-6 col-sm-offset-6'>" +
            "<label>Subject</label>     :     <input type='text' value='' readonly name='subject' class='form-control coll'/><br>" +
            "<label>Type of Test:</label>" +
            "<select name='category' class='form-control'>" +
            "<option value=''>-- Select Type--</option>" +
            "<option value='Quiz'>Quiz</option>" +
            "<option value='Worksheet'>Worksheet</option>" +
            "<option value='Sliptest'>Sliptest</option>" +
            "<option value=''Monthly test'>Monthly test</option>" +
            "<option value='Term1'>Term1</option>" +
            "<option value='Term2'>Term2</option>" +
            "<option value='Term3'>Term3</option>" +
            "</select><br>" +
            "<label>Total Marks</label>      :     <input type='number' name='total_marks' id='total_marks' value='' min='0' class='form-control coll' /><br> " +
            "<label>Actual Marks</label>      :     <input type='number' name='obtained_marks' id='obtained_marks' value='' min='0' class='form-control coll'/> <br>" +
            "<label>Is Present :</label>" +
            "<input type='radio' name='is_present' value='Yes' class='coll' style='margin-left:20px;' checked='checked'/> Yes" +
            "<input type='radio' name='is_present' value='No' class='coll' style='margin-left:20px;' /> No <br>" +
            "<label>Assessed date</label>      :     <input  name='date_created'  value=''  class='form-control coll datepicker'/> <br>" +
            "</div>" +
            "<div class=' col-sm-offset-1 col-sm-10 'style='position:absolute; bottom:75px;' >" +
            "<button type='submit' class='btn btn-success btn-sm sch_fm_sub' style='width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspSubmit</button>" +
            "<button style='display:inline; float:right' class='btn btn-danger btn-sm can_sch'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "</div>" +
            "</form> ";

        var schol_lfh_form = "<form><div class='col-sm-offset-1 col-sm-10 lr_tables col-sm-offset-1' style='margin-bottom:10px;'>" +
            "<div style='max-height:400px;height:380px;'>" +
            "<p style='text-align:center;font-weight:bold'>Scholastic LFH Details</p>" +
            "<p style='color:red;text-align:center;display:none' class='err_msg' >Please enter Required Fields...</p>" +
            "<div class='cosch ' style='max-height:280px;' >" +
            "</div>" +
            "<div class='col-sm-offset-2 col-sm-8 col-sm-offset-2 lr_tables' style='margin-bottom:10px;'>" +
            "<label>Subject</label>     :     <input type='text' value='' readonly name='subject' class='form-control coll'/><br>" +
            "<label>Topics</label>: <select name='topics' id='lfh_topics' class='form-control'>"
            // "<% _.forEach(resp2.data,function(u,i){ %>"+
            // "<% if(i == 'all_topics'){ %>"+
            // "<% _.forEach(u, function(uu){ %>+<option value='<%=uu%>' ><%=uu%></option>"
            // "<%  }); %> "+
            // "<%}%>"+
            // "<%});%>"+
            // "</div></div></div></form>"


        var co_schol_form = "<form>" +
            "<h5 style='font-weight:bold;text-align:center;margin-bottom:10px;'>Co-Scholastic Form<h5>" +
            "<p style='color:red;text-align:center;display:none' class='err_msg'>Please enter Required Fields...</p>" +
            "<div class='col-sm-offset-1 col-sm-5 '>" +
            "<select name='lr_initiativeness' style='margin:20px 0px' class='form-control'>" +
            "<option value=''>-- Initiativeness --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='lr_responsibility'  style='margin:20px 0px' class='form-control'>" +
            "<option value='Responsibility'>-- Responsibility --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='lr_supportiveness'  style='margin:20px 0px' class='form-control'>" +
            "<option value=''>-- Supportiveness --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='pr_attentiveness' style='margin:20px 0px'   class='form-control'>" +
            "<option value=''>-- Attentiveness --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='pr_curious' style='margin:20px 0px'   class='form-control'>" +
            "<option value=''>-- Curious --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='pr_self_confidence' style='margin:20px 0px'   class='form-control'>" +
            "<option value=''>-- Self Confidence --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "</div>" +
            "<div class='col-sm-5  '>" +
            "<select name='ee_emotional_connect'  style='margin:20px 0px' class='form-control'>" +
            "<option value=''>-- Emotional Connect --</option>" +
            "<option value='excellent'>excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='ee_technology_exposure' style='margin:20px 0px'   class='form-control'>" +
            "<option value=''>-- Technology Exposure --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='ee_widerperspective' style='margin:20px 0px'  class='form-control'>" +
            "<option value=''>-- Wider Perspective --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='bh_courteousness'  style='margin:20px 0px' class='form-control'>" +
            "<option value=''>-- Courteousness --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<select name='bh_positive_attitude'  style='margin:20px 0px'  class='form-control'>" +
            "<option value=''>-- Positive Attitude --</option>" +
            "<option value='Excellent'>Excellent</option>" +
            "<option value='Very Good'>Very Good</option>" +
            "<option value='Good'>Good</option>" +
            "<option value='Average'>Average</option>" +
            "<option value='Needs Improvement'>Needs Improvement</option>" +
            "<option value='Not Observed'>Not Observed</option>" +
            "</select>" +
            "<input   value='' placeholder='Assessed Date' name='date_created'   class='form-control datepicker'/><br>" +
            "</div>" +
            "<div class=' col-sm-offset-1 col-sm-10 'style='position:absolute; bottom:75px;' >" +
            "<button type='submit' class='btn btn-success btn-sm co_sch_fm_sub' style='width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspSubmit</button>" +
            "<button style='display:inline; float:right' class='btn btn-danger btn-sm can_cosch'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "</div>" +
            "</form> ";


        var act_form = "<form>" +
            "<h5 style='font-weight:bold;text-align:center;margin-bottom:10px;'>Activities Form<h5>" +
            "<p style='color:red;text-align:center;display:none'  class='err_msg'>Please enter Required Fields...</p>" +
            "<div class='col-sm-offset-3 col-sm-6 col-sm-offset-6'>" +
            "<label>Notes</label>     :     <textarea  value='' name='notes' class='form-control'/><br>" +
            "<label>Grading</label>      :     <input type='text' name='grading'  value=''  class='form-control' /><br> " +
            "<label>Assessment Date</label>     : <input   value=''   placeholder='Assessed Date' name='date_created'   class='form-control datepicker'/><br>" +
            "</div>" +
            "<div class=' col-sm-offset-1 col-sm-10 'style='position:absolute; bottom:75px;' >" +
            "<button type='submit' class='btn btn-success btn-sm  act_fm_sub' style='width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspSubmit</button>" +
            "<button style='display:inline; float:right' class='btn btn-danger btn-sm can_act'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "</div>" +
            "</form> ";
        var uc_form = "<form>" +
            "<h5 style='font-weight:bold;text-align:center;margin-bottom:10px;'>Unique Charasterstics Form<h5>" +
            "<p style='color:red;text-align:center;display:none;' class='err_msg' >Please enter Required Fields...</p>" +
            "<div class='col-sm-offset-3 col-sm-6 col-sm-offset-6'>" +
            "<label>Strengths</label>     :     <textarea  value='' name='strengths'  class='form-control'/><br>" +
            "<label>Weaknessess</label>     :     <textarea  value=''  name='weaknesses' class='form-control'/><br>" +
            "<label>Assessment Date</label> : <input value=''   placeholder='Assessed Date' name='date_created'   class='form-control datepicker'/><br>" +
            "</div>" +
            "<div class=' col-sm-offset-1 col-sm-10 'style='position:absolute; bottom:75px;' >" +
            "<button type='submit' class='btn btn-success btn-sm  uc_fm_sub' style='width:100px;'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspSubmit</button>" +
            "<button style='display:inline; float:right' class='btn btn-danger btn-sm   can_uc'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "</div>" +
            "</form> ";

        var diag_form2 = "<form class='form-inline diag_form'>" +
            "<h5 style='font-weight:bold;text-align:center;margin-bottom:10px;'>Diagnostic Form</h5><br>" +
            "<p style='color:red;text-align:center;display:none;' class='err_msg' >Please enter Required Fields...</p>" +
            "<div class='row'>" +
            "<div class='col-sm-offset-1 col-sm-10 col-sm-offset-1'>" +
            "<label>Aggregate level</label>     :     <input type='text' style='width:150px' value=''  name='agg_level' class='form-control inlin'/>" +
            "<label style='margin-left:14%;'>Assessment Date</label> : <input value=''  style='width:150px'  placeholder='Assessed Date' name='date_created'   class='form-control datepicker inlin'/><br><br>" +
            "<label>Diagnostic Details :</label><br><br>" +
            "<div style='height:240px;overflow-y:auto;'> " +
            "<table class='table table-condensed' style='font-size:12px;'>" +
            "<tr>" +
            "<th>Code</th>" +
            "<th>Parameter</th>" +
            "<th>Level</th>" +
            "<th>Total Marks</th>" +
            "<th>Actual Marks</th>" +
            "</tr>" +
            "<%_.forEach(resp3.param_list,function(u){%>" +
            "<tr>" +
            "<td><%=u.param_code%></td>" +
            "<td><%=u.name%></td>" +
            "<td><%=u.level%></td>" +
            "<td><%=u.total_marks%></td>" +
            "<td><input class='form-control inlin' type='number' value='' min='0' max='200' style='width:75px;height:27px' name='<%=u.param_code%>' /></td>" +
            "</tr>" +
            "<%})%>" +
            "</table>" +


            "</div>" +
            "</div>" +
            "</div>" +

            "<div class=' col-sm-offset-1 col-sm-10 'style='position:absolute;padding:0px; bottom:75px;' >" +
            "<button type='submit' class='btn btn-success btn-sm  diag_fm_sub' style='width:100px'><i class='glyphicon glyphicon-upload'></i>&nbsp&nbspSubmit</button>" +
            "<button style='display:inline; float:right' class='btn btn-danger btn-sm  can_diag'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>" +
            "</div>" +
            "</form> ";

        //award tab:
        var awards_temp = "<div style='text-align:center;background-color:#27A3E2;display:none;color:white;padding:10px;' id='status_msg'></div><div class='col-md-5'>" +
            "<div class='award_list'>" +
            "<% _.forEach(resp2.data.award_list, function(award){ %>" +
            "<div class='award_item <% if(_.contains(resp2.data.selected_list, award.name)){ %> award_item_selected <% } %>'><%= award.name %></div>" +
            "<% }); %>" +
            "</div>" +
            "<div class='nominate btn btn-success'>Nominate</div>" +
            "</div>" +
            "<div class='col-md-7'>" +
            "<div class='table-responsive'>" +
            "<table class='table table-striped table-bordered table-condensed'>" +
            "<thead><tr class='btn-success'>" +
            "<th>Award</th>" +
            "<th>Nominated by</th>" +
            "</tr></thead>" +
            "<tbody>" +
            "<% _.forEach(resp2.data.stud_nominations, function(award){ %>" +
            "<tr>" +
            "<td><%= award.award %></td>" +
            "<td><%= award.teacher %></td>" +
            "</tr>" +
            "<% }); %>" +
            "</tbody>" +
            "</table>" +
            "</div>" +
            "</div>";

        var attendance_temp = "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Attendance Details</p>" +
            "          <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:420px;;margin-bottom:10px;'>" +
            "          <table class='table table-striped table-hover'>" +
            "               <th>Month</th><th>Present</th><th>Absent</th><th>Total</th>" +
            "               <% _.forEach(resp2.data, function(uuu){  %>  " +
            "                   <tr><td><%= uuu.month %></td><td><%= uuu.present %></td><td><%= uuu.absent %></td><td><%= uuu.total %></td></tr>" +
            "               <% }) %>  " +
            "          </table>" +
            "          </div>       ";

        var appreciation_temp = "<div>" +
            "<div class='row col-md-12'>" +
            "<% _.forEach(resp2.data, function(uuu){ if (uuu.stic_ids){ %> " +
            "<span class='col-md-2' style='float:right;' ><img title='<%= uuu.stic_name %>' src='/<%= uuu.sticker_path %>' style='width: 25%;height: 4%;margin-left: 15%;margin-top: 0%;' />:<span  class = 'stic_count'><%= uuu.stic_ids %> </span></span>" +
            " <% }}) %>  " +
            "<div class='row col-md-12'><span class='col-md-6'>" +
            "<label>Select the Reason:<span style='color: red'>*</span></label>" +
            "<select class='form-control' id ='dropDownId'>" +
            "               <% _.forEach(resp2.data, function(uuu){ if (uuu.reason){  %>  " +
            "                  <option value=<%= uuu.appreciation_id %>> <%= uuu.reason %> </option> " +
            "               <% }}) %>  " +
            "<option value='others'>others</option> " +
            "</select></span><span class='col-md-6'><label class='show_label' style='color: black;display: none;' >Add Custom Reason:<span style='color: red'>*</span></label><input type ='text' class='form-control show_label' placeholder='Please add the reason' id='add_other_reason' value='' onkeyup='changevalue(this,this.id)' style='display:none;margin-top:1%;width:100%;' /></span></div></br>" +
            "      <div style ='margin-top: 1%;' class='form-group col-md-8'><label for='comments'>Comments:</label><textarea class='form-control' rows='4' id='comments' value='' onkeyup='changevalue(this, this.id)' ></textarea></div>" +
            "<% if (resp2.data){%><div style='margin-top:10%;'><div class='col-md-12'>" +
            "<label id ='sticker_id'>Select an Appreciation Sticker:<span style='color: red'>*</span></label>" +
            "<div class ='row' style ='margin-top: 3%;'>" +
            "<div class='sticker_div'>" +
            "               <% _.forEach(resp2.data, function(uuu){ if(uuu.sticker_id){ %>  " +
            "<img style='display: inline-block; width: 75px;height: 75px;border-radius: 50%;MARGIN-LEFT: 20PX;' onclick='makeActive(<%= uuu.sticker_id %>)' id='<%= uuu.sticker_id %>' class='sticker' title=''src='/<%= uuu.sticker_path %>'>" +
            "               <% }}) %>  " +
            "</div>" +
            "</div><% } %>" +
            //                         " else{ %>"+
            //                         "<div style='margin-top:10%;'> <p>No stickers found </p></div>"+
            //                         "<%} %> "+
            "<div class='row' align='center'><button id='submit_btn' type='button' class='btn btn-success btn-sm' style='margin-left:10px;width:100px;margin-top: 10px;'>&nbsp&nbspSubmit</button></div></div>";

        var assign_temp = "<div>" +
            "<ul class='nav nav-tabs assign_div' style='padding-left:200px;'>" +
            " <li role='presentation'><a class='stud_assign_sub'>Submitted</a></li>" +
            " <li role='presentation'><a class='stud_assign_rev'>Reviewed</a></li>" +
            " <li role='presentation'><a class='stud_assign_res'>Resubmit</a></li>" +
            " <li role='presentation'><a class='stud_assign_comp'>Completed</a></li>" +
            "</ul>" +
            "</div>";

        var assign_status_sub = "<p style='text-align:center;margin:40px 0px;font-weight:bold'>Submitted Assignments</p>";

        var assign_status_res = "<p style='text-align:center;margin:40px 0px;font-weight:bold'>Resubmit Assignments</p>";

        var assign_status_rev = "<p style='text-align:center;margin:40px 0px;font-weight:bold'>Reviewed Assignments</p>";

        var assign_status_comp = "<p style='text-align:center;margin:40px 0px;font-weight:bold'>Completed Assignments</p>";

        var assign_status_com_temp = "          <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:auto;height:320px;;margin-bottom:10px;'>" +
            "          <table class='table table-striped table-hover'>" +
            "               <th style='text-align:center;'>Assignment no</th><th style='text-align:center;'>Added on</th><th style='text-align:center;'>Assignment Id</th><th style='text-align:center;'>Assignment File</th><th style='text-align:center;'>Edit</th>" +
            "               <% _.forEach(resp2.results, function(uuu){  %>  " +
            "                   <tr><td style='text-align:center;'><%= uuu.assignment_no %></td><td style='text-align:center;'><%= uuu.added_on %></td><td style='text-align:center;'><%= uuu.homework_id %></td><td style='text-align:center;'><a href=\'<%= uuu.file_path %><%= uuu.file_name %>\' target='_blank'><i class='glyphicon glyphicon-download-alt'> Download</i></a></td><td><button onclick='updateAssignmentStatus(\"<%= uuu.student_id %>\", \"<%= uuu.session_id %>\", \"<%= uuu.assignment_no %>\", \"<%= uuu.status %>\")'><i class='glyphicon glyphicon-edit'></i></button></td></tr>" +
            "               <% }) %>  " +
            "          </table>" +
            "          </div>       ";
        
        var quiz_temp = " <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1' style='overflow-y:hidden;height:430px;;margin-bottom:10px;' > " +
            "<p style='text-align:center;margin:20px 0px;font-weight:bold'>Quiz Result</p>" +
            "<div style='max-height:350px;height:330px;overflow-y:auto;'>" +
            "          <table class='table table-striped table-hover' style='max-height:300px;'> " +
            "               <th style='text-align:center;'>Attempt</th><th style='text-align:center;'>Offering Id</th><th style='text-align:center;'>Total question</th><th style='text-align:center;'>No of question correct</th><th style='text-align:center;'>Date Taken</th> " +
            "               <% _.forEach(resp2.data, function(u){  %>  " +
            "                   <tr><td style='text-align:center;'><%= u.attempt%></td><td style='text-align:center;'><%= u.offer_id%></td><td style='text-align:center;'><%= u.numOfQuestions%></td><td style='text-align:center;'><%= u.numOfCorrectAns %></td><td style='text-align:center;'><%= u.date %></td></tr> " +
            "               <% }) %>  " +
            "          </table> " +
            " </div> " +
            "          </div>       ";

            
        var form_array = [schol_form, co_schol_form, act_form, uc_form, diag_form2, schol_lfh_form];
        var temp_array = [scol_temp, coscol_temp, act_temp, uc_temp, diag_temp, report_temp, awards_temp, attendance_temp, appreciation_temp, schol_lfh_temp, assign_temp, assign_status_sub, assign_status_res, assign_status_rev, assign_status_com_temp, assign_status_comp,quiz_temp];

        //console.time('ConcatTimer');
        $('#student_details').hide();
        $('#loader').show();
        //processing response
        var ay_html = "";
        var offer_html = "<option value='empty' data-ay='ay'>--- Select an Offer ---";
        var stud_html = "";
        resp1 = resp;
        var t1 = _.template(" <%  _.forEach(resp1.offerings, function(u,i){  %> " +
            "   <div class='offer_stud' id='offer_<%= u.offer_id%>' <% if(i!=0){ %> style='display:none;' <%}%> > " +
            "   <% _.forEach(u.offer_en_stud, function(uu,i){  %>  " +
            "    <div class='stud_details_block' id='stud_<%= uu.stud_id %>' <% if (i!=0){%> style='display:none;' <%}%> > " +
            "      <div class='row hdr' >  " +
            "          <div class='col-sm-2' style='padding-top:10px;' > " +
            "             <img class='img-responsive img-thumbnail thumb'   src='/<%= uu.stud_photo %>'  />  " +
            "          </div>  " +
            "      <div class='col-sm-5' style='padding-top:10px;'>  " +
            "             <label>Name :</label><p style='display:inline;padding-left:10px;'> <%= uu.stud_name %> </p><br> " +
            "              <label>Grade :</label><p style='display:inline'> <%= uu.stud_grade %>  </p><br> " +
            "              <label>Gender :</label><p style='display:inline'> <%= uu.stud_gender %></p><br> " +
            "              <label>center :</label><p style='display:inline'> <%=uu.stud_center%></p><br> " +
            "       </div> " +
            "       <div class='col-sm-5' style='padding-top:10px;'> " +
            "              <label>School RollNo :</label><p style='display:inline'> <%= uu.stud_sch_rollno %></p><br> " +
            "              <label>eVidyaloka ID :</label><p style='display:inline;'> <%= uu.stud_id %></p><br> " +
            "              <label>Father Occupation :</label><p style='display:inline;padding-left:10px;'> <%= uu.stud_fath_occ %></p><br> " +
            "              <label>Mother Occupation :</label><p style='display:inline;'> <%= uu.stud_moth_occ %>  </p><br> " +
            "       </div> " +
            "       </div> " +
            "      <div class='row sectns' style='padding-top:15px;margin-bottom:20px;font-size:13px;'> " +
            "         <div class=' col-sm-12' > " +
            "             <ul class='nav nav-tabs mystudent_nav' data-offer='<%= u.offer_id %>' data-id='<%= uu.stud_id %>' > " +
            "                 <li role='presentation'  <% if (tab_id=='my_stud_teach'){%> class='active' <%}%> ><a  class='stud_att'  id='att_<%=uu.stud_id %>_<%=u.offer_id%>'>Attendance</a></li> " +
            "                 <li role='presentation'><a  class='stud_schol'  >Scholastic</a></li> " +
            "                 <li role='presentation'><a  class='stud_schol_lfh'  >Scholastic-LFH</a></li> " +
            "                 <li role='presentation'><a  class='stud_coschol'  >Co-Scholastic</a></li> " +
            "                 <li role='presentation'><a  class='stud_act'  >Activities</a></li> " +
            "                 <li role='presentation'><a  class='stud_uc'>Unique Characterstics</a></li> " +
            "                 <li role='presentation'><a  class='stud_diag' >Diagnostics</a></li> " +
            "                 <li role='presentation'><a  class='stud_report' >Reports</a></li> " +
            "                 <li role='presentation'><a  class='stud_awards' >Awards</a></li> " +
            "                 <li role='presentation' <% if (tab_id!='my_stud_teach'){%> class='active' <%}%>><a  class='stud_appre' >Appreciation</a></li> " +
            "                 <li role='presentation'><a  class='stud_assign'>Assignments</a></li> " +
            "                 <li role='presentation'><a  class='stud_quiz_result'>Quiz Result</a></li> " +
            "             </ul> " +
            "         </div> " +
            "      </div> " +
            "      <div class='row arena1 slides' style='display:none' >" +
            "          <div class='col-sm-offset-1 col-sm-10 col-sm-offset-1 lr_tables' style='overflow-y:auto;height:435px;;margin-bottom:10px;' id='lr_<%= uu.stud_id %>'>" +
            "            <table class='table table-striped table-hover'>" +
            "            </table>" +
            "          </div>" +
            "      </div>" +
            "      <div class='row arena2 slides'>" +
            "      </div>" +
            "      <div class='row arena3 slides'>" +
            "      </div>" +
            "      <div class='row arena4 slides'>" +
            "      </div>" +
            "      <div class='row arena5 slides'>" +
            "      </div>" +
            "      <div class='row arena6 slides'>" +
            "      </div>" +
            "      <div class='row arena7 slides' data-stud='<%= uu.stud_id %>' data-sub='<%=u.offer_name%>' data-offer='<%=u.offer_id%>' >" +
            "      </div>" +
            "      <div class='row arena8 slides' >" +
            "      </div>" +
            "      <div class='row arena9 slides' >" +
            "      </div>" +
            "      <div class='row arena10 slides' >" +
            "      </div>" +
            "      <div class='row arena11 slides' >" +
            "      </div>" +
            "      <div class='row arena12 slides' >" +
            "      </div>" +
            "      <div class='row arena13 slides'  data-stud_id='<%= uu.stud_id %>' data-offer='<%=u.offer_id%>'>" +
            "      </div>" +
            "      <div class='row arena14 slides' >" +
            "      </div>" +
            "      <div class='row arena16 slides' >" +
            "      </div>" +
            "     </div> " +
            "      <div class='row arena15' >" +
            "      </div>" +
            "    <% }) %> </div>" +
            "    <% }) %>  ");
        if (typeof resp1 == 'object') {
            t1(resp1.offerings);
        } else {
            alert(resp1);
            $('#loader').hide();
        }
        var offer_stud_html = "";
        resp.offerings.forEach(function() {
            var curr = arguments[0];
            stud_html = "";
            offer_html += '<option value=' + curr.offer_id + ' data-ay=' + curr.offer_ay_id + ' >' + curr.offer_name + '</option> ';
            curr.offer_en_stud.forEach(function() {
                var curr1 = arguments[0];
                stud_html += '<li class="list-group-item stud_ent" style="cursor:pointer;padding:4px 15px;" data-offer=' + curr.offer_id +
                    ' data-id=' + curr1.stud_id + ' data-ay_id=' + curr.offer_ay_id + ' > ' + curr1.stud_name + '</li>'
            });
            offer_stud_html += '  <ul class="list-group stud_lists"  data-len="' + curr.offer_en_stud.length + '" id="students_list_' + curr.offer_id + '_' + curr.offer_ay_id + '"  style="display:none;max-height:460px;overflow-y:auto;"> ' + stud_html + ' </ul> ';
        });
        //AY dropdown
        resp.ay_list.forEach(function() {
            var curr = arguments[0];
            ay_html += '<option value=' + curr.ay_id + '>' + curr.ay_title + ' ' + curr.ay_board + '</option>';
        });

        $('#student_details').html(t1);
        $('#sel_offer').html(offer_html);
        $('#sel_ay').html(ay_html);
        $('#sel_offer').change(function() {
            var ay_id = $('#sel_ay').val();
            var tmp = "#students_list_" + $(this).val() + "_" + ay_id;
            $('.stud_lists').hide();
            var first = $(tmp).slideDown().find('.stud_ent').first();
            first.css({ 'background-color': '#F15A22', 'color': 'white' });
            disp(first);
            $('#stud_badge').text($(tmp).data('len') || 0);
        });

        //$('#sel_ay option[value="' + resp1.current_ay + '"]').prop("selected", true);
        setTimeout(function() { $('#sel_ay').val(resp1.current_ay).trigger('change'), 0 });
        //on change AY:
        $("body").on("change", "#sel_ay", function() {
            var ofr_id = $("#sel_offer").val();
            var ay_id = $(this).val();
            var offer_count = 0;
            var flag = true;
            $("#sel_offer > option").each(function() {
                if ($(this).attr("data-ay") === ay_id) {
                    $(this).css("display", "block");
                    if (flag) {
                        $(this).prop("selected", true);
                        flag = false;
                    }
                    offer_count++;
                } else if ($(this).attr("data-ay") === 'ay') {
                    $(this).prop("selected", true);
                } else {
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
        setTimeout(function() {
            var disp = $("#sel_offer option:nth-child(2)").css("display");
            if (disp === "none") {
                $("#sel_offer").val("empty").trigger("change");
            } else {
                $("#sel_offer").val($("#sel_offer option:nth-child(2)").val()).trigger("change");
            }
        }, 0);
        //$("#sel_offer option:nth-child(2)").attr("selected",true);
        //$('#students').find('.stud_lists').first().show().find('.stud_ent').first().css({'background-color':'#F15A22', 'color':'white'});
        $(".mystudent_nav").find("li").find("a").css({ 'padding': '8px 12px', 'margin-right': '0' });
        $('#students').find('.stud_ent').click(function() {
            var ele = $(this);
            disp(ele);
        });
        // Caching responses

        var resp_dict = {};
        var template_dict = {};

        function render_resp(resp, temp_dict, stud_id, offer_id) {
            var stu_id = stud_id;
            var off_id = offer_id;
            var ky = stu_id + '_' + off_id;
            if (_.has(temp_dict, ky)) {
                temp = temp_dict.ky;
                return temp;
            } else {
                templt = _.template();

            }

        }


        //diagnostics form 
        //Diagnostics switch

        // Report Fetch
        $('a.stud_att').click(function() {
            create_slide(this, temp_array[7]);
        });
        $('a.stud_coschol').click(function() {
            create_slide(this, temp_array[1]);
        });
        $('.arena5,.arena8,.arena1, .arena12').on('click', '.cositem', function() {
            $(this).siblings().removeClass('active');
            $(this).addClass('active');
            var ele = '#' + $(this).data('id');
            var ances = $(this).closest('.slides').find('.cosch');
            $(ances).children('.details').hide().removeClass('active');
            $(ances).children(ele).show().addClass('active');
        });

        $('a.stud_uc').click(function() {
            create_slide(this, temp_array[3]);
        });

        $('a.stud_act').click(function() {
            create_slide(this, temp_array[2]);
        });
        $('a.stud_schol').click(function() {
            create_slide(this, temp_array[0]);
        });
        $('a.stud_diag').click(function() {
            create_slide(this, temp_array[4]);
        });
        $('a.stud_report').click(function() {
            create_slide(this, temp_array[5]);
        });
        $('a.stud_awards').click(function() {
            create_slide(this, temp_array[6]);
        });
        $('a.stud_appre').click(function() {
            create_slide(this, temp_array[8]);
        });
        $('a.stud_schol_lfh').click(function() {
            create_slide(this, temp_array[9]);
        });
        $('a.stud_assign').click(function() {
            create_slide(this, temp_array[10]);
        });
        $('.arena13').on('click', '.stud_assign_sub', function() {
            create_slide(this, temp_array[11] + temp_array[14]);
        });
        $('.arena13').on('click', '.stud_assign_rev', function() {
            create_slide(this, temp_array[13] + temp_array[14]);
        });
        $('.arena13').on('click', '.stud_assign_res', function() {
            create_slide(this, temp_array[12] + temp_array[14]);
        });
        $('.arena13').on('click', '.stud_assign_comp', function() {
            create_slide(this, temp_array[15] + temp_array[14]);
        });
        $('a.stud_quiz_result').click(function() {
            create_slide(this, temp_array[16]);
        });
        // Scholatic lfh edit and update
        $(".slides").on("click", ".editor_sch_lfh", function() {
            var that = $(this).closest('.slides').find('.details.active').find('.edit');
            if (that.text()) {
                that.each(function() {
                    var orig_content = $(this).text();
                    html_data = "<select style='height: 30px;border-radius: 3px;background-color: #fff;'><option value='" + orig_content.trim() + "'>" + orig_content.trim() + "</option><option value='"
                    if (this.id == 'outcome') {
                        if (orig_content.trim() == 'Correct') {
                            html_data += "Incorrect'>Incorrect</option>"
                        } else {
                            html_data += "Correct'>Correct</option>"
                        }
                        html_data += "</select>"
                    } else if (this.id == 'is_present') {
                        if (orig_content.trim() == 'Yes') {
                            html_data += "No'>No</option>"
                        } else {
                            html_data += "Yes'>Yes</option>"
                        }
                        html_data += "</select>"
                    } else if (this.id == 'record_typ') {
                        if (orig_content.trim() == 'Baseline') {
                            html_data += "Endline'>Endline</option>"
                        } else {
                            html_data += "Baseline'>Baseline</option>"
                        }
                    } else if (this.id == 'record_dt') {
                        html_data = "<input type='date' name='baseline_endline'  value='" + orig_content.trim() + "'  class='form-control coll datepicker'/>"
                    }
                    $(this).html(html_data);
                });
                $(this).parent().prev().find('.subject_list').find('.cositem').addClass('disabled').removeClass('cositem')
                $(this).hide().siblings('.update_sch_lfh,.cancel_sch_lfh').show();
            } else {
                alert("No data to update")
            }
        });

        $('.slides').on('click', '.cancel_sch_lfh', function() {
            $(this).hide().siblings('.editor_sch_lfh,.update_sch_lfh').toggle();
            $(this).closest('.arena12').siblings('.sectns').find('a.stud_schol_lfh').click();
        });

        //Scholastic Edit and update
        $(".slides").on("click", ".editor_sch", function() {
            var that = $(this).closest('.slides').find('.details.active').find('.edit');
            if (that.text()) {
                that.each(function() {
                    var orig_content = $(this).text();
                    $(this).html("<input type='number' style='width:100px;height:30px' min='0' max='100' class='form-control' value='" + Number(orig_content) + "'/>");
                });
                $(this).parent().prev().find('.subject_list').find('.cositem').addClass('disabled').removeClass('cositem')
                $(this).hide().siblings('.update_sch,.cancel_sch').show();
            } else {
                alert("No data to update")
            }
        });
        $('.slides').on('click', '.cancel_sch', function() {
            $(this).hide().siblings('.editor_sch,.update_sch').toggle();
            $(this).closest('.arena1').siblings('.sectns').find('a.stud_schol').click();
        });
        $('.slides').on('click', '.update_sch', function() {
            var that = $(this).closest('.slides').find('.details.active').find('tr').not(':eq(0)');
            var that1 = $(this);
            var up_list = []
            that.each(function() {
                tds = $(this).find('td');
                var rec = { 'id': $(this).data('id'), 'total': $(tds[2]).find('input').val(), 'actual': $(tds[3]).find('input').val() };
                up_list.push(rec)
            });
            breakOut = false
            $.each(up_list, function(key, value) {
                if (parseInt(value["total"]) < parseInt(value["actual"])) {
                    breakOut = true;
                    return false;
                }
            });
            if (breakOut) { alert('Actual or obtained marks can not be higher than total marks'); } else {
                $.post('/update_lrs/', { 'up_list': JSON.stringify(up_list) }, function(resp) {
                    $(that1).closest('.arena1').siblings('.sectns').find('a.stud_schol').click();
                }).done(function() { alert('Updated Successfully'); });
            }
        });

        $('.slides').on('click', '.update_sch_lfh', function() {
            var that = $(this).closest('.slides').find('.details.active').find('tr').not(':eq(0)');
            var that1 = $(this);
            var up_list = []
            that.each(function() {
                tds = $(this).find('td');
                var rec = { 'id': $(this).data('id'), 'outcome': $(tds[2]).find('select').val(), 'is_present': $(tds[3]).find('select').val(), 'record_type': $(tds[4]).find('select').val(), 'record_date': $(tds[5]).find('input').val() };
                up_list.push(rec)
            });
            $.post('/v2/update_scholastic_lfh/', { 'scholastic_lfh_data': JSON.stringify(up_list) }, function(resp) {
                $(that1).closest('.arena12').siblings('.sectns').find('a.stud_schol_lfh').click();
            }).done(function() { alert('Updated Successfully'); });
        });
        $('.arena7').on('click', 'input[type=radio]', function() {
            var present = $(this).val();
            if (present == 'Yes') {
                $('#obtained_marks').attr("disabled", false);
                $("#obtained_marks").val("");
            } else {
                $("#obtained_marks").val("0");
                $('#obtained_marks').attr("disabled", true);
            }
        });

        //Co-Scholastic Edit and update


        $(".slides").on("click", ".editor_cosch", function() {
            var that = $(this).closest('.slides').find('.details.active').find('.edit');
            that.each(function() {
                var orig_content = $(this).text();
                // $(this).html("<input type='text' style='width:170px;height:30px;' class='form-control' value='"+ orig_content +"'/>");
                $(this).html('<select class="form-control">' +
                    '<option value="Excellent">Excellent</option>' +
                    '<option value="Very Good">Very Good</option>' +
                    '<option value="Good">Good</option>' +
                    '<option value="Average">Average</option>' +
                    '<option value="Needs Improvement">Needs Improvement</option>' +
                    '<option value="Not Observed">Not Observed</option>' +
                    '<select>').find('select').val(orig_content);
                //$(this).find('select').val(orig_content);
            });
            $(this).parent().siblings('.cosch_list').find('.cositem').addClass('disabled').removeClass('cositem');
            $(this).hide().siblings('.update_cosch,.cancel_cosch').show();
        });
        $('.slides').on('click', '.cancel_cosch', function() {
            $(this).hide().siblings('.editor_cosch,.update_cosch').toggle();
            $(this).closest('.arena5').siblings('.sectns').find('a.stud_coschol').click();
        });
        $('.slides').on('click', '.update_cosch', function() {
            var that2 = $(this).closest('.slides').find('.details.active');
            var that1 = $(this);
            var that = that2.find('tr').not(':eq(0)');
            rec = {};
            rec.id = that2.data('id');
            that.each(function() {
                tds = $(this).find('td');
                rec[($(tds[0]).text())] = $(tds[1]).find('select').val();
            });
            $.post('/update_cosch/', { 'rec': JSON.stringify(rec) }, function(resp) {
                $(that1).closest('.arena5').siblings('.sectns').find('a.stud_coschol').click();
            }).done(function() { alert('Updated Successfully'); });
        });
        //Activities edit and update
        $(".slides").on("click", ".editor_act", function() {
            var that = $(this).closest('.slides').find('table').find('.edit');
            that.each(function() {
                var orig_content = $(this).text();
                if ($(this).hasClass('inn')) {
                    $(this).html("<input style='width:100px;' class='form-control'  value='" + orig_content + "'/>");
                } else {
                    $(this).html("<textarea style='width:250px;' class='form-control' rows='3' >" + orig_content + "</textarea>");
                }
            });
            $(this).hide().siblings('.update_act,.cancel_act').show();
        });
        $('.slides').on('click', '.cancel_act', function() {
            $(this).hide().siblings('.editor_act,.update_act').toggle();
            $(this).closest('.arena3').siblings('.sectns').find('a.stud_act').click();
        });
        $('.slides').on('click', '.update_act', function() {
            var that = $(this).closest('.slides').find('table').find('tr').not(':eq(0)');
            var that1 = $(this);
            var up_list = []
            that.each(function() {
                tds = $(this).find('td');
                var rec = { 'id': $(this).data('id'), 'notes': $(tds[0]).find('textarea').val(), 'grading': $(tds[1]).find('input').val() };
                up_list.push(rec)
            });
            $.post('/update_act/', { 'up_list': JSON.stringify(up_list) }, function(resp) {
                $(that1).closest('.arena3').siblings('.sectns').find('a.stud_act').click();
            }).done(function() { alert('Updated Successfully'); });
        });
        //UniqueC edit and update
        $(".slides").on("click", ".editor_uc", function() {
            var that = $(this).closest('.slides').find('table').find('.edit');
            that.each(function() {
                var orig_content = $(this).text();
                $(this).html("<textarea style='width:180px;' class='form-control' rows='3' >" + orig_content + "</textarea>");
            });
            $(this).hide().siblings('.update_uc,.cancel_uc').show();
        });
        $('.slides').on('click', '.cancel_uc', function() {
            $(this).hide().siblings('.editor_uc,.update_uc').toggle();
            $(this).closest('.arena4').siblings('.sectns').find('a.stud_uc').click();
        });
        $('.slides').on('click', '.update_uc', function() {
            var that = $(this).closest('.slides').find('table').find('tr').not(':eq(0)');
            var that1 = $(this);
            var up_list = [];
            that.each(function() {
                tds = $(this).find('td');
                var rec = { 'id': $(this).data('id'), 'strengths': $(tds[0]).find('textarea').val(), 'weaknesses': $(tds[1]).find('textarea').val() };
                up_list.push(rec)
            });
            $.post('/update_uc/', { 'up_list': JSON.stringify(up_list) }, function(resp) {
                $(that1).closest('.arena4').siblings('.sectns').find('a.stud_uc').click();
            }).done(function() { alert('Updated Successfully'); });
        });

        //Diagnostics edit and update
        $(".slides").on("click", ".editor_diag", function() {
            var that = $(this).closest('.slides').find('.details.active').find('table').find('.edit');
            that.each(function() {
                var orig_content = $(this).text();
                $(this).html("<input type='number' style='width:100px;height:30px;' min='0' max='100' class='form-control'  value='" + Number(orig_content) + "'/>");
            });
            $(this).hide().siblings('.update_diag,.cancel_diag').show();
        });
        $('.slides').on('click', '.cancel_diag', function() {
            $(this).hide().siblings('.editor_diag,.update_diag').toggle();
            $(this).closest('.arena8').siblings('.sectns').find('a.stud_diag').click();
        });
        $('.slides').on('click', '.update_diag', function() {
            var that = $(this).closest('.slides').find('.details.active').find('table').find('tr').not(':eq(0)');
            var that1 = $(this);
            var up_list = [];
            that.each(function() {
                tde = $(this).find('td.edit');
                var rec = { 'id': $(this).data('id'), 'actual_marks': $(tde).find('input').val() };
                up_list.push(rec)
            });
            $.post('/update_diag/', { 'up_list': JSON.stringify(up_list) }, function(resp) {
                $(that1).closest('.arena8').siblings('.sectns').find('a.stud_diag').click();
            }).done(function() { alert('Updated Successfully'); });
        });


        //Create new lrs

        $('.slides').on('click', '.add_sch, .add_sch_lfh,.add_co_sch,.add_act,.add_uc,.add_diag', function() {
            if ($(this).hasClass('add_sch')) {
                var arna = $(this).closest('.slides');
                arna.hide().siblings('.arena7').show().html(form_array[0]);
                var targ = arna.siblings('.arena7');
                targ.find('form').find('input[name=subject]').val(targ.data('sub'));
            } else if ($(this).hasClass('add_sch_lfh')) {
                html_data = form_array[5];
                for (index in global_response['data']['all_topics']) {
                    html_data += "<option value=" + resp2['data']['all_topics'][index]['id'] + " >" + resp2['data']['all_topics'][index]['title'] + "</option>"
                }
                html_data += "</select><br><label>Outcome :</label><input type='radio' name='outcome' value='Correct' class='coll' style='margin-left:20px;' checked='checked'/> Correct"
                html_data += "<input type='radio' name='outcome' value='Incorrect' class='coll' style='margin-left:20px;' /> Incorrect <br><br>"
                html_data += "<label style='padding-right:0%'>Is Present :</label>"
                html_data += "<input type='radio' name='is_present' value='Yes' class='coll' style='margin-left:12px;' checked='checked'/> Yes"
                html_data += "<input type='radio' name='is_present' value='No' class='coll' style='margin-left:42px;' /> No <br><br>"
                html_data += "<input type='radio' name='record_type' value='Baseline' class='coll' style='margin-left:0px;' checked='checked'/> Baseline"
                html_data += "<input type='radio' name='record_type' value='Endline' class='coll' style='margin-left:20px;' /> Endline <br><br>"
                html_data += "<label>Accessed date :</label>"
                html_data += "<input type='date' name='accessed_date'  value=''  class='form-control coll'/> <br></div>"
                html_data += "<div class='row' style='bottom:0;position:absolute;width:96%;'>"
                html_data += "<button type='submit' class='btn btn-success btn-sm lfh_sch_fm_sub' style='width:100px;position:relative;left:22px;'>&nbsp&nbspSubmit</button>"
                html_data += "<button type='button' class='btn btn-danger btn-sm cancel_add_sch_lfh' style='width:100px; float:right;'><i class='glyphicon glyphicon-remove'></i>&nbsp&nbspCancel</button>"
                html_data += "</div></div>"
                var arna = $(this).closest('.slides');
                arna.hide().siblings('.arena7').show().html(html_data);
                var targ = arna.siblings('.arena7');
                targ.find('form').find('input[name=subject]').val(targ.data('sub'));
            } else if ($(this).hasClass('add_co_sch')) {
                $(this).closest('.slides').hide().siblings('.arena7').show().html(form_array[1]);
            } else if ($(this).hasClass('add_act')) {
                $(this).closest('.slides').hide().siblings('.arena7').show().html(form_array[2]);
            } else if ($(this).hasClass('add_uc')) {
                $(this).closest('.slides').hide().siblings('.arena7').show().html(form_array[3]);
            } else if ($(this).hasClass('add_diag')) {
                var that = $(this);
                var dta = $(this).closest('.slides').siblings('.arena7');
                var offer = dta.data('offer');
                var stud = dta.data('stud');
                var html_diag_form = '';
                $.post('/get_diag_params/', { 'stud': stud, 'offer': offer }, function(resp) {
                    if (typeof resp == 'object') {
                        resp3 = resp
                        var diag_form = _.template(form_array[4]);
                        diag_form(resp3.param_list);
                        $(that).closest('.slides').hide().siblings('.arena7').show().html(diag_form);
                        $('.datepicker').each(function() {
                            $(this).datepicker({ maxDate: 0 });
                        });

                    } else {
                        var html_error = '<p style="margin-top:180px;text-align:center;color:red">' + resp + '</p>';
                        $(that).closest('.slides').hide().siblings('.arena7').show().html(html_error);
                    }

                });
            }
            $('.datepicker').each(function() {
                $(this).datepicker({ maxDate: 0 });
            });

        });


        $('.arena7').on('click', 'button', function(e) {
            e.preventDefault();
            var elem = $(this);
            if ($(this).hasClass('sch_fm_sub')) {
                val_sub(this, 'Scholastic');
            } else if ($(this).hasClass('lfh_sch_fm_sub')) {
                val_sub(this, 'Scholastic-LFH');
            } else if ($(this).hasClass('co_sch_fm_sub')) {
                val_sub(this, 'Co-scholastic');
            } else if ($(this).hasClass('act_fm_sub')) {
                val_sub(this, 'Activity');
            } else if ($(this).hasClass('uc_fm_sub')) {
                val_sub(this, 'Uniquec');
            } else if ($(this).hasClass('diag_fm_sub')) {
                val_sub2(this, 'Diagnostic');
            }

            //Handling 
            if ($(this).hasClass('can_sch')) {
                $(this).closest('.slides').hide().siblings('.arena1').show();
            } else if ($(this).hasClass('cancel_add_sch_lfh')) {
                $(this).closest('.slides').hide().siblings('.arena12').show();
            } else if ($(this).hasClass('can_cosch')) {
                $(this).closest('.slides').hide().siblings('.arena5').show();
            } else if ($(this).hasClass('can_act')) {
                $(this).closest('.slides').hide().siblings('.arena3').show();
            } else if ($(this).hasClass('can_uc')) {
                $(this).closest('.slides').hide().siblings('.arena4').show();
            } else if ($(this).hasClass('can_diag')) {
                $(this).closest('.slides').hide().siblings('.arena8').show();
            }
            //diagnostic new diag details group addition
            if (elem.hasClass('add_grp')) {
                var par = $(this).parent();
                var cln = par.clone();
                cln.find('input').each(function() { $(this).val(''); })
                cln.insertAfter(par);
                par.find('.add_grp').removeClass('btn-info add_grp').addClass('btn-danger rem_grp').find('i').removeClass('glyphicon-plus').addClass('glyphicon-minus');
            } else if (elem.hasClass('rem_grp')) {
                $(this).parent().remove();
            }
        });

        //Custom Functions
        //Validation and submit
        var val_sub = function(that, type) {
            var ret = validate(that);
            if (ret == true && type == "Scholastic-LFH") {
                var fom = $(that).closest('form');
                var data = get_data(fom, type);
                response = post_data('/v2/add_lfh_scholastics/', data);
                $(that).closest('.slides').siblings('.sectns').find('li.active').find('a').click();
            } else if (ret == true && type != "Scholastic") {
                var fom = $(that).closest('form');
                var data = get_data(fom, type);
                response = post_data('/add_lr/', data);
                $(that).closest('.slides').siblings('.sectns').find('li.active').find('a').click();
            } else if (ret == true) {
                var total_marks = document.getElementById("total_marks").value;
                var obtained_marks = document.getElementById("obtained_marks").value;
                if (parseInt(total_marks) >= parseInt(obtained_marks)) {
                    var fom = $(that).closest('form');
                    var data = get_data(fom, type);
                    response = post_data('/add_lr/', data);
                    $(that).closest('.slides').siblings('.sectns').find('li.active').find('a').click();
                } else {
                    alert("Actual or obtained marks can not be higher than total marks")
                }
            }
        }

        var val_sub2 = function(that, type) {
            var ret = validate(that);
            if (ret == true) {
                var fom = $(that).closest('form');
                var data = get_data2(fom);
                response = post_data('/add_diagnostic/', data);
                $(that).closest('.slides').siblings('.sectns').find('li.active').find('a').click();
            }
        }

        var get_data2 = function(fom) {
            var arena = $(fom).parent();
            var form_data = $(fom).serializeArray();
            var post_data = {};
            var coll_data = {};
            $(form_data).each(function() {
                coll_data[this.name] = this.value;
            });
            post_data['student_id'] = arena.data('stud');
            post_data['offering_id'] = arena.data('offer');
            post_data['agg_level'] = coll_data['agg_level'];
            post_data['date_created'] = coll_data['date_created']
            delete coll_data['agg_level'];
            delete coll_data['date_created'];
            post_data['child_data'] = JSON.stringify(coll_data);
            return post_data;
        }

        //Form data Collection
        var get_data = function(fom, type) {
                var arena = $(fom).parent();
                var form_data = $(fom).serializeArray();
                var post_data = {};
                var coll_data = {};
                $(form_data).each(function() {
                    coll_data[this.name] = this.value;
                });
                post_data['student_id'] = arena.data('stud');
                post_data['offering_id'] = arena.data('offer');
                post_data['category'] = type;
                post_data['child_data'] = JSON.stringify(coll_data);
                return post_data;
            }
            // Post Data
        var post_data = function(url, data) {
                var response = "";
                $.post(url, data, function(resp) { response = resp; });
                return response;
            }
            //Form validation
        var validate = function(ele) {
                var fm = ele.closest('form');
                var flds = $(fm).find('.form-control');
                var er_msg = $(fm).find('.err_msg');
                var count = 0;

                flds.each(function() {
                    if ($(this).val() != "") { count++; }
                });
                if (count < flds.length) { $(er_msg).slideDown(); return false; } else { $(er_msg).slideUp(); return true; }
            }
            //displays  first particular element of student details block
        var disp = function(ele) {
            ele.parent().find('.stud_ent').css({ 'background-color': '', 'color': 'black' });
            ele.css({ 'background-color': '#F15A22', 'color': 'white' }).addClass("active_stud");
            var ofr = '#offer_' + ele.data('offer');
            var stu_id = '#stud_' + ele.data('id');
            var tab = get_curr_tab();
            $('.offer_stud').hide();
            $('.stud_details_block').removeClass('activ');
            $(ofr).slideDown().find('.stud_details_block').hide();
            $(ofr).find(stu_id).slideDown().addClass('activ').find('.sectns').find('a').filter('.' + tab).click();
        }

        //displays corresponding slide
        var disp_slide = function(block, slide) {
            var ele1 = $(block).parent('li');
            ele1.siblings().removeClass('active');
            ele1.addClass('active');
            var ele = $(block).closest('.sectns');
            ele.siblings('.slides').hide();
            ele.siblings(slide).show();

        }

        var get_curr_tab = function() {
                var tab = $('.stud_details_block').filter('.activ').find('.sectns').find('li.active').find('a').attr('class');
                if (!tab)
                    if (tab_id == 'my_stud_teach')
                        tab = 'stud_att';
                    else
                        tab = 'stud_appre';
                    //console.log(tab);
                return tab;
            }
            //rendering
        var global_response;
        var create_slide = function(that, templatee) {
                var url = "";
                var target = "";
                var type = "";
                if ($(that).hasClass('stud_schol')) {
                    url = '/get_scholastic/';
                    target = '.arena1';
                } else if ($(that).hasClass('stud_schol_lfh')) {
                    url = '/get_scholastic_lfh/';
                    target = '.arena12';
                } else if ($(that).hasClass('stud_coschol')) {
                    url = '/get_co_schol/';
                    target = '.arena5';
                } else if ($(that).hasClass('stud_act')) {
                    url = '/get_activities/';
                    target = '.arena3';
                } else if ($(that).hasClass('stud_uc')) {
                    url = '/get_uniquec/';
                    target = '.arena4';
                } else if ($(that).hasClass('stud_diag')) {
                    url = '/get_diagnostics/';
                    target = '.arena8';
                } else if ($(that).hasClass('stud_report')) {
                    url = '/get_reports/';
                    target = '.arena9';
                } else if ($(that).hasClass('stud_awards')) {
                    url = '/get_award_nominees/';
                    target = '.arena10';
                } else if ($(that).hasClass('stud_att')) {
                    url = '/get_month_attend/';
                    target = '.arena2';
                } else if ($(that).hasClass('stud_appre')) {
                    url = '/get_appreciation_reason/';
                    target = '.arena11';
                } else if ($(that).hasClass('stud_assign')) {
                    url = '';
                    target = '.arena13';
                } else if ($(that).hasClass('stud_assign_sub')) {
                    var student_id = $(that).parent().parent().parent().parent().data('stud_id');
                    var stud_offer = $(that).parent().parent().parent().parent().data('offer');
                    url = '/api/student/uploaded/assignments/status?student_id=' + student_id + '&status=Submitted&offering_id=' + stud_offer;
                    target = '.arena14';
                    type = 'get';
                } else if ($(that).hasClass('stud_assign_res')) {
                    var student_id = $(that).parent().parent().parent().parent().data('stud_id');
                    var stud_offer = $(that).parent().parent().parent().parent().data('offer');
                    url = '/api/student/uploaded/assignments/status?student_id=' + student_id + '&status=Resubmit&offering_id=' + stud_offer;
                    target = '.arena14';
                    type = 'get';
                } else if ($(that).hasClass('stud_assign_rev')) {
                    var student_id = $(that).parent().parent().parent().parent().data('stud_id');
                    var stud_offer = $(that).parent().parent().parent().parent().data('offer');
                    url = '/api/student/uploaded/assignments/status?student_id=' + student_id + '&status=Reviewed&offering_id=' + stud_offer;
                    target = '.arena14';
                    type = 'get';
                } else if ($(that).hasClass('stud_assign_comp')) {
                    var student_id = $(that).parent().parent().parent().parent().data('stud_id');
                    var stud_offer = $(that).parent().parent().parent().parent().data('offer');
                    url = '/api/student/uploaded/assignments/status?student_id=' + student_id + '&status=Completed&offering_id=' + stud_offer;
                    target = '.arena14';
                    type = 'get';
                } else if ($(that).hasClass('stud_quiz_result')) {
                    url = '/get_quiz_result/';
                    target = '.arena16';
                }
                var temp = $(that).parent().parent();
                var stud_id = temp.data('id');
                var offer_id = temp.data('offer');
                var kyy = stud_id + '_' + offer_id;

                if (type == 'get') {
                    $.get(url, function(resp) {
                        resp2 = resp;
                        global_response = resp2
                        var templ_c = _.template(templatee);
                        templ_c(resp2.results);
                        $("#dropDownId").val('null');
                        $(that).closest('.row').siblings(target).html(templ_c);
                        $(target).css({ 'display': 'block' });
                    });
                } else {
                    $.post(url, { 'stud_id': stud_id, 'offer_id': offer_id, 'csrfmiddlewaretoken': csrftoken }, function(resp) {
                        resp2 = resp;
                        global_response = resp2
                        var templ_c = _.template(templatee);
                        templ_c(resp2.data);
                        $("#dropDownId").val('null');
                        $(that).closest('.row').siblings(target).html(templ_c);
                    });
                }
                //    debugger;
                disp_slide($(that), target);


            } //end function
    }).done(function() { $('#student_details').show();
        $('#loader').hide(); });

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

    //onclick award_item
    $("body").on("click", ".award_item", function() {
        if ($(this).hasClass("award_item_selected")) {
            $(this).removeClass("award_item_selected");
        } else {
            $(this).addClass("award_item_selected");
        }
    }); //end click award

    $("body").on("click", "#submit_btn", function() {

        var reason_id = $('select#dropDownId option:selected').val();

        //var sticker_id = $("#checkboxId:checked").val();
        var sticker_id = $('.sticker_div').find('.stickerActive').attr('id');
        $.each($("li.stud_ent"), function() {
            if ($(this).css("color") === 'rgb(255, 255, 255)') {
                student_id = $(this).attr("data-id");
                offer_id = $(this).attr("data-offer");
            }
        });


        var other_reason = $('#add_other_reason').val();

        var comments = $('#comments').val();

        if (reason_id == 'null') {
            alert("please select the reason");

        }

        //var number_of_checked_checkbox= $("input[name=checkbox]:checked").length;
        var sticker_length = $('.sticker_div').find('.stickerActive').length;
        // console.log("sticker_length",sticker_length);
        if (sticker_length == 0) {
            alert("select the sticker");
        }

        //    alert("reason_id "+reason_id + ", sticker_id "+sticker_id +", other_reason "+other_reason+" , comments "+ comments)

        if (reason_id && sticker_id) {
            $.post("/v2/ajax/submittAppreciation/", {
                "appreciationId": reason_id,
                "volunteerId": student_id,
                "offering_id": offer_id,
                "stickerId": sticker_id,
                "otherReason": other_reason,
                "comment": comments,
                "reason_type": "appreciation",
                "for_whom": "student"
            }, function(resp) {
                alert(resp);
                $("#dropDownId").val('null');
            });
        }

    });


    $("body").on("click", "#dropDownId", function() {
        val = $('select#dropDownId option:selected').val();
        if (val == 'others') {
            $('.show_label').css('display', 'block');
        } else {
            $('.show_label').css('display', 'none');
        }
    });

    $("body").on("change", '#checkboxId', function() {
        $('.checkbox').not(this).prop('checked', false);
    });


    //nominate
    $("body").on("click", ".nominate", function() {
        var that = $(this);
        that.html("Processing...").removeClass("btn-success").addClass("btn-danger");
        selected_list = []
        $.each($(this).parent().children(".award_list").children(".award_item"), function() {
            if ($(this).hasClass("award_item_selected")) {
                selected_list.push($(this).html());
            }
        });
        //student_id = $(".sectns").find(".mystudent_nav").attr("data-id");
        //offer_id   = $(".sectns").find(".mystudent_nav").attr("data-offer");
        $.each($("li.stud_ent"), function() {
            if ($(this).css("color") === 'rgb(255, 255, 255)') {
                student_id = $(this).attr("data-id");
                offer_id = $(this).attr("data-offer");
            }
        });
        //console.log(selected_list);
        $.get('/save_nomination/', { 'student_id': student_id, 'offer_id': offer_id, 'selected_list': selected_list }, function(resp) {
            that.parent().parent().children("#status_msg").text("Updated Successfully").slideDown(350).slideUp(300);
            //$('a.stud_awards').trigger("click");
            setTimeout(function() { $('a.stud_awards').trigger("click") }, 1000);
        }); //end ajax calll

    }); //end nominate click
}); // end document ready

function changevalue(e, id) {
    var value = $(e).val();
    $('#' + id).val(value).trigger('change');
}

function makeActive(id) {
    // alert(id);
    $('.sticker_div').find('.stickerActive').removeClass('stickerActive');
    $('.sticker_div').find("#" + id).toggleClass('stickerActive');
}

function updateAssignmentStatus(stu_id, sess_id, assign_no, assign_status) {
    //  console.log(stu_id, sess_id, assign_no, assign_status);
    cell_html = "<div class='row' style='padding : 0px 20px 20px 0px;'>";
    cell_html += "<label for='status_remarks_choose' style='color:black; width: 100%;position: relative;left:2%;'>Choose Status : </label><br>";
    cell_html += "<input name='status_button' style='color:black; width: 5%;position: relative;top:5%; left:5%' type='radio' id='status_button_completed' value='Completed'><label for='status_button_completed' style='color:black; width: 45%;position: relative;top:5%;left:5%;'>Completed</label><br>";
    cell_html += "<input name='status_button' style='color:black; width: 5%;position: relative;top:10%; left:5%' type='radio' id='status_button_reviewed' value='Reviewed'><label for='status_button_reviewed' style='color:black; width: 45%;position: relative;top:10%;left:5%;'>Reviewed</label><br>";
    cell_html += "<input name='status_button' style='color:black; width: 5%;position: relative;top:10%; left:5%' type='radio' id='status_button_resubmit' value='Resubmit'><label for='status_button_resubmit' style='color:black; width: 45%;position: relative;top:10%;left:5%;'>Resubmit</label><br><hr>";
    cell_html += "<label for='status_remarks' style='color:black; width: 45%;position: relative;left:2%;'>Remarks : </label><br><textarea type='text' style='color: black;width: 90%; padding: 10px 20px 10px 20px; margin: 2%; display: inline-block; border: 1px solid #ccc; border-radius: 4px;box-sizing: border-box;' id='status_remarks' placeholder='Remarks...' />";
    cell_html += "<button class='btn btn-success pull-right' onclick=updateAssignment(" + stu_id + "," + sess_id + "," + assign_no + ");>Update</button>";
    // console.log(cell_html);
    // console.log(cell_html_footer);
    $('#student_assignment_modal').html(cell_html);
    // $('#student_assignment_modal_footer').html(cell_html_footer);
    // $('#studentAssignmentModal').modal('show');
    document.getElementById('studentAssignmentModal').style.display = 'block';

}

function updateAssignment(stu_id, sess_id, assign_no) {
    if (confirm("Are You Sure?")) {
        assign_status = $("input[name='status_button']:checked").val();
        var assign_remarks = $("#status_remarks").val();
        $.post('/api/update_status_and_remarks/', { 'student_id': stu_id, 'session_id': sess_id, 'assignment_no': assign_no, 'status': assign_status, 'remarks': assign_remarks }, function(resp) {
            alert(resp['data']['message']);
            // $('#studentAssignmentModal').modal('hide');
            document.getElementById('studentAssignmentModal').style.display = 'none';
            if (assign_status == 'Submitted') {
                $('.stud_assign_sub').trigger('click');
            } else if (assign_status == 'Resubmit') {
                $('.stud_assign_res').trigger('click');
            } else if (assign_status == 'Reviewed') {
                $('.stud_assign_rev').trigger('click');
            } else if (assign_status == 'Completed') {
                $('.stud_assign_comp').trigger('click');
            }
        });
    }
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}