        $(document).ready(function(){

            $("[rel=tooltip]").tooltip();
            {% if show_error_msg %}
                evd.show_msg("Please update your profile");
            {% endif %}
            var hash = window.location.href.split("?")[1];
            if(hash == "offerings"){
                $(".db-3").trigger("click");
            }else if(hash == "preferences"){
                $(".db-2").trigger("click");
            }else if(hash == "readiness")
                $(".db-4").trigger("click");
            if($(".item.active").position().left != 0)
                $(".item.active").css({"left": "0px"});

           var country = "{{ user_profile.country}}";
           $("select[name='country']").children("option[value='"+ country +"']").attr({"selected": "selected"});

           var $from_date = $("input[name='from_date']"),
               $to_date = $("input[name='to_date']");

           var time_zone = "{{user_profile.time_zone}}";
           $("select[name='time_zone']").children("option[value='"+ time_zone + "']").attr({"selected" : "selected"});
 
           var from_date = parseInt($from_date.attr("data-from_date_ts")) - 31800000;
           var curr_date = from_date == "" ?new Date():new Date(from_date),
                curr_day = curr_date.getDate(),
                curr_month = curr_date.getMonth() + 1,
                curr_year = curr_date.getFullYear(),
                min_date = curr_year +"-"+ curr_month +"-"+ curr_day;
           window.min_start_date = curr_date;


           var future_date = new Date(curr_date.getTime()+3628800000),
                future_day = future_date.getDate(),
                future_month = future_date.getMonth() + 1,
                future_year = future_date.getFullYear(),
                max_date = future_year +"-"+ future_month +"-"+ future_day;
           window.min_end_date = future_date;

            $from_date.datepicker({
                dateFormat: "yy-mm-dd",
                minDate: min_date
            });
            $to_date.datepicker({
                dateFormat: "yy-mm-dd",
                minDate: max_date
            });

            var pref_subjects = "{{ user_profile.pref_subjects }}";
            pref_subjects = pref_subjects.split(";");
            for( var subject in pref_subjects )
            {
                sub = pref_subjects[ subject ];
                $(".prefered_subjects input[type='checkbox']").each(function(){
                    if($(this).attr("value") == sub){
                        $(this).attr("checked","checked");
                    }
                });
            }

            var status = "{{ user_profile.status }}";
            $("select[name='status']").children("option").each(function(){
                if($(this).val() == status){
                    $(this).attr("selected", "selected");
                }
            });

            var pref_roles = [{% for role in pref_roles %}{{role}}{% if not forloop.last %},{% endif %}{% endfor %}];
            for( var role in pref_roles )
            {
                $("#prefered_roles input[type='checkbox']").each(function(){
                    if($(this).attr("value") == pref_roles[role]){
                        $(this).attr("checked","checked");
                    }
                });
            }

            var pref_medium = "{{ user_profile.pref_medium }}";
            pref_medium = pref_medium.split(";");
            for( var medium in pref_medium )
            {
                $("#medium").children("option[value='" + pref_medium[medium] + "']").attr({"selected":"selected"});
            }

            var reference_channel = "{{ user_profile.reference_channel }}";
            $("select[name='reference_channel']").children("option[value='" + reference_channel + "']").attr({"selected": "selected" });

            var pref_offerings = [{% for offering in  user_profile.pref_offerings.all %}"{{ offering.id }}"{% if not forloop.last %},{% endif %}{% endfor %}];
            for( var offering in pref_offerings )
            {
                $("#offerings-table input[type='checkbox']").each(function(){
                    if($(this).attr("value") == pref_offerings[offering]) {
                        $(this).attr("checked","checked");
                    }
                });
            }

           $("div.profile-pic-wrapper").mouseenter(function(){
                $(this).children(".caption").addClass("show").css({"margin-top" : "-32px"});
           });
           $("div.profile-pic-wrapper").mouseleave(function(){
                $(this).children(".caption").css({"margin-top" : "0px"}).removeClass("show");
           });

            $("li.dropdown, ul.dropdown-menu").mouseenter(function(){
                $(this).children("ul.dropdown-menu").show();
            });
            $("li.dropdown, ul.dropdown-menu").mouseleave(function(){
                $(this).children("ul.dropdown-menu").hide();
            });

            $(".back-btn").click(function(){
                var tab = $(this).attr("data-tab");
                $("."+tab).trigger("click");
            });

        });

