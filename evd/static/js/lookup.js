        $(document).ready(function(){
            $(".date-picker").datepicker({
                dateFormat: "dd-mm-yy",
                onSelect: function(datatext, inst){
                    var data = encodeURIComponent(datatext),
                        $target = $("#date-from"),
                        href = $target.attr("href");
                    href.replace(/(?:(?:\?|&)from=([^&$]*))/,function(matched,captured){
                        if(captured.length > 0)
                            var new_part = matched.replace(captured,data);
                        else
                            var new_part = matched + data;
                        href = href.replace(matched,new_part);
                    });
                    if($(inst.input).attr("placeholder") == "available upto"){
                        $target = $("#date-to");
                        href = $target.attr("href");
                        href.replace(/(?:(?:\?|&)to=([^&$]*))/,function(matched,captured){
                            if(captured.length > 0)
                                var new_part = matched.replace(captured,data);
                            else
                                var new_part = matched + data
                            href = href.replace(matched,new_part);
                        });
                    }
                    $target.attr({"href": href});
                    $target.trigger("click");
                }
            });
            $(".date-picker").change(function(){
                var $target = "",
                    href = "";
                if($(this).attr("placeholder") == "available from") {
                    $target = $("#date-from"),
                    href = $target.attr("href");
                    var value = $(this).val();
                    href.replace(/(?:(?:\?|&)from=([^&$]*))/,function(matched,captured){
                        if(value != "")
                            if(captured.length > 0)
                                var new_part = matched.replace(captured,value);
                            else
                                var new_part = matched + value
                        else
                            if(captured.length > 0)
                                var new_part = matched.replace(captured,"all");
                            else
                                var new_part = matched + "all";
                        href = href.replace(matched,new_part);
                    });
                }
                else {
                     $target = $("#date-to");
                     href = $target.attr("href");
                     var value = $(this).val();
                     href.replace(/(?:(?:\?|&)to=([^&$]*))/,function(matched,captured){
                        if(value != "")
                            if(captured.length > 0)
                                var new_part = matched.replace(captured,value);
                            else
                                var new_part = matched + value
                        else
                            if(captured.length > 0)
                                var new_part = matched.replace(captured,"all");
                            else
                                var new_part = matched + "all";
                        href = href.replace(matched,new_part);
                     });
                }
                $target.attr({"href": href});
                $target.trigger("click");
            });

            var enabled = function(){
                $(this).find("a.btn").show();
            };
            $("#content").on("click", ".user-block", enabled);
            $("#html").not(".user-block").click(function(){
                $(".user-block a.btn").hide();
            });
            $("#content").on("mouseover", ".user-block", function(){
                $("[rel=tooltip]").tooltip();
            });
        $("#send-mail-modal").on("show", function(){
            var url = "/get_user_emails/?"+links[1];
            $.get(url,function(resp){
                $("#send-mail-modal img").fadeOut(function(){
                    var $form = $(this).next("div");
                    $form.fadeIn();
                    $form.find("textarea[name='user_emails']").val(resp);
                });
            })
        });
        $("#send-mail-modal").on("hide", function(){
            $("#send-mail-modal img").show();
            $("#send-mail-modal img").next("div").hide();
        });

        });

