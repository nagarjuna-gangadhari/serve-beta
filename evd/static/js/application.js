(function($){
    window.evd = window.evd || {};
    window.evd.init = function(){

        // footer fix for big screens
        var adjust_footer = function(){
        }

        var cycler = function($cycle, cycle_step, direction){
            cycle_step = cycle_step || 0;
            direction = direction || "next";
            var $children = $cycle.children(),
                cycle_count = $children.length,
                $next_cycle = $cycle.next("ul");
            if(direction == "next"){
                var index = $children.index($children.filter(".active").last()) + 1;
            }
            else {
                var index = $children.index($children.filter(".active").last()) - cycle_step;
                index = index >= 0 ? index: cycle_count + index;
            }
            $next_cycle.empty();
            $children.filter(".active").removeClass("active");
            for(var i = 0; i < cycle_step; i++)
            {
                var $li = $children.eq(index++%cycle_count).addClass("active").clone("false");
                $next_cycle.append($li);
            }
        };
        $(".prev").click(function(e){
            var $cycle = $($(this).attr("rel")),
                step = parseInt($(this).attr("data-step")),
                direction = "prev";
            if($cycle.children().length > step){
                cycler.apply(null,[$cycle, step, direction]);
            }
            else
                $(this).hide();
        });
        $(".next").click(function(e){
            var $cycle = $($(this).attr("rel")),
                step = parseInt($(this).attr("data-step")),
                direction = "next";
            if($cycle.children().length > step){
                cycler.apply(null,[$cycle, step, direction]);
            }
            else
                $(this).hide();
        });

        // end cycle code


        // baloon code
        var show_msg = function(msg){
                $("#evd-notification .msg-body").text(msg);
                var $that = $("[id=\"evd-notification\"]").removeClass("hide").slideDown();
                if(arguments[1]){
                    window.setTimeout(function(){
                        $that.slideUp();
                    },arguments[1]);
                }
           },
           hide_msg = function(){
                $("[id=\"evd-notification\"]").addClass("hide").slideUp();
           };

        $("[id=\"evd-notification\"] .close").click(function(){
            hide_msg();
        });

        var clear_form_elements = function(ele) {
            $(ele).find(':input').each(function() {
                switch(this.type) {
                    case 'password':
                    case 'select-multiple':
                    case 'select-one':
                    case 'text':
                    case 'textarea':
                        $(this).val('');
                        break;
                    case 'checkbox':
                    case 'radio':
                        this.checked = false;
                }
            });
        },
        validate_form = function(form){
           var $form = form || this,
               reg_map = {
                         not_empty: { regex: /\S/, message: "this field cannot be empty" },
                         skype_id: { regex: /\S/, message: "invalid skype id" },
                         password: { regex: /(.+){5,}/, message: "password is weak" },
                         username: { regex: /^[A-Za-z0-9.]+$/, message: "invalid username" },
                         us_phone_number: { regex: /^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$/, message: "not a valid us phone number" },
                         indian_phone_number: { regex: /^(\+?\d{2})?\d{10,}$/, message: "not a valid phone number"},
                                                                                                                                                                                   us_date: { regex: /^\d{1,2}-\d{1,2}-\d{4}$/, message: "not a valid date"},
                                                                                                                                                                                   email: { regex: /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/, message: "not a valid email id" }
                                                                                                                                                                           };
           var valid = true;
           $.each($form.find("[data-validate=true]"),function(){
               var field_type = $(this).attr("data-field-type").split(";"),
                   show_tooltip = $(this).attr("data-show-tooltip"),
                   $that = $(this);
               $.each(field_type,function(i,v){
                   if(reg_map[v] && !reg_map[v].regex.test($that.val())){
                       if(show_tooltip == "true") {
                            $that.tooltip("destroy");
                            $that.tooltip({ title: reg_map[v].message });
                            $that.tooltip("show");
                            /*
                            $that.focus(function(){
                                //$that.removeAttr("rel", "data-placement", "data-original-title");
                                $that.tooltip("destroy");
                            });*/
                            $that.keydown(function(){
                                $that.tooltip("destroy");
                            });
                       }
                       else {
                           $that.val("");
                           $that.watermark(reg_map[v].message);
                           $that.css({"border": "1px solid #790471"});
                           $that.focus(function(){
                               $that.css({"border": "1px solid #ccc"});
                           });
                       }
                       valid = false;
                   }
                   else{
                       valid = valid && true;
                   }
                    return valid;
               });
           });
           return valid;
        },
        ajax_link = function(e){
            var pre_call = $(this).attr("pre-call"),
                callback = $(this).attr("callback"),
                $label = $(this).find(".ajax-button-label"),
                old_text = $label.text(),
                loading_text = $label.attr("data-loading")?$label.attr("data-loading"):"processing",
                continue_process = true;

            if(evd[pre_call]){
                continue_process = evd[pre_call].apply(this);
                continue_process = continue_process == undefined?true:continue_process;
            }
            //$label.text(loading_text);
            if(continue_process == false ){
                e.preventDefault();
                return
            }


            var url = $(this).attr("href"),
                that = this;

            $.get(url, function(resp){
                if(evd[callback])
                    evd[callback].apply(that,[resp]);
                //$label.text(old_text);
            });
            e.preventDefault();
        },


        called_already = false ;
        ajax_submit = function(e){
            if (called_already == true)
                return ;
            else
                called_already = true ;
            var pre_call = $(this).attr("pre-call"),
            continue_process = true;
            if($(this).attr("validate") == "true"){
               continue_process = validate_form.apply($($(this).attr("href")));
            }
            if(continue_process && window.evd[pre_call]){
                continue_process = window.evd[pre_call].apply(this, [e]);
                continue_process = continue_process == undefined?true:continue_process;
            }
            if(continue_process == false ){
               e.preventDefault();
               return
            }
            var $form = $($(this).attr("href")),
                data = $form.serialize(),
                method = $form.attr("method").toUpperCase(),
                url = $form.attr("action"),
                cb = $(this).attr("callback"),
                that = this,
                $label = $(this).find(".ajax-button-label");
                old_text = $label.text(),
                loading_text = $label.attr("data-loading")?$label.attr("data-loading"):"processing";

                $label.text(loading_text);
            if(method=="POST")
            {
                $.ajax({
                    url: url,
                    type: "POST",
                    data: data
                })
                .done(function(resp) {
                    if(window.evd[cb]){
                            window.evd[cb].apply(that,[resp]);
                    }
                    /*
                    after_success_text = $label.attr("data-after-success")?$label.attr("data-after-success"):old_text;
                    $label.text(after_success_text);
                    */
                })
                .fail(function(){
                     alert("Error has occured.Request failed");
                     $label.text(old_text);
                })
            }
            else{
               /* $.get(url, data, function(resp){
                    if(window.evd[cb]){
                        window.evd[cb].apply(that,[resp]);
                    }
                    $label.text(old_text);
                });*/
                $.ajax({
                    url: url,
                    type: "GET",
                    data: data
                })
                .done(function(resp){
                    if(window.evd[cb]){
                        window.evd[cb].apply(that,[resp]);
                    }
                    after_success_text = $label.attr("data-after-success")?$label.attr("data-after-success"):old_text;
                    $label.text(after_success_text);
                })
                .fail(function(){
                    alert("Error has occured.Request failed");
                    $label.text(old_text);
                })
            }
            e.stopPropagation();
            e.preventDefault();
        };

        // watermarking for IE
        var apply_watermark = function(){
            var watermark = $(this).attr("placeholder");
            if(watermark)
                $(this).watermark(watermark);
        }

        $.each($("input"), apply_watermark);
        $.each($("textarea"), apply_watermark);


        $("a[rel='ajax-link']").click(ajax_link);
        $("[rel='submit']").click(ajax_submit);
        $("[rel='submit']").each(function(e){
            $($(this).attr("href")).submit(function(e){
                ajax_submit.apply($(this).find("[rel='submit']")[0], [e]);
                e.preventDefault();
            });
        });
        $("#login-signup-form input").bind("focusin", function(){
            if(window.form_status == "signup")
                if($.support.transition)
                    $(this).parent().next("small").slideDown("fast");
                else
                    $(this).parent().next("small").show();
        });
        $("#login-signup-form input").bind("focusout", function(){
            if(window.form_status == "signup")
                if($.support.transition)
                    $(this).parent().next("small").slideUp("fast");
                else
                    $(this).parent().next("small").hide()
        });

        adjust_footer();

        return {
            ajax_submit   : ajax_submit,
            ajax_link     : ajax_link,
            validate_form : validate_form,
            clear_form    : clear_form_elements,
            show_msg      : show_msg,
            hide_msg      : hide_msg,
            cycler        : cycler,
            ajust_footer  : adjust_footer
        }
    };
}(jQuery));

$(document).ready(function () {
    window.sub=0;
    $('.profile_pic').on('mouseover',function () {
            $('.sub_logout').css('display', 'block');
    });
        $('.sub_logout').on('mouseover',function(){
            window.sub = 1;
        });
        $('.sub_logout').on('mouseleave',function(){
            window.sub=0;
            $('.sub_logout').css('display', 'none');
        });
    });
        if(window.sub==0){
            $('.sub_logout').css('display', 'none');
        }
    $("html").on("click", function(){
        $('.sub_logout').css('display', 'none');
    });


