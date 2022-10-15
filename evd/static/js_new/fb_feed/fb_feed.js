
   (function($){

    var total_post = []
    $.fn.evdFacebook = function(options){
        var wall = this;
        options = options || {};

        options = $.extend({
            limit: 30,   // You can also pass a custom limit as a parameter.
        },options);

        var graphUSER = 'https://graph.facebook.com/'+options.id+'/?fields=name,picture&access_token='+options.member_token,
            graphPOSTS = 'https://graph.facebook.com/'+options.id+'/feed/?fields=picture,name,message,link,icon,from,created_time,id,source,story&access_token='+options.member_token+'&date_format=U&limit='+options.limit;

        var render_wall = function(graphUSER,graphPOSTS){
                //var wall = this;
                $.when($.getJSON(graphUSER),$.getJSON(graphPOSTS)).done(function(user,posts){
                    // user[0] contains information about the user (name and picture);
                    // posts[0].data is an array with wall posts;
                    var fb = {
                        user : user[0],
                        posts : []
                    };
                    $.each(posts[0].data,function(){
                        // We only show links and statuses from the posts feed:
                        if(!this.message){
                            return true;
                        }

                        // Copying the user avatar to each post, so it is
                        // easier to generate the templates:
                        this.userpicture = fb.user.picture.data.url;
                        // Converting the created_time (a UNIX timestamp) to
                        // a relative time offset (e.g. 5 minutes ago):
                        this.created_time = relativeTime(this.created_time*1000);
                        // Converting URL strings to actual hyperlinks:
                        this.message = urlHyperlinks(this.message);
                        fb.posts.push(this);
                    });
                    total_post.push(fb);
                    if (members_len[0].fb_id === options.id) {
                      if (members_len.length === 1) {
                        var final_posts_data = post_template_data(total_post[0],options)
                        $('.render_feed').append(final_posts_data);  
                        // if user has no posts then posting all beats of evidyaloka posts
                      } else if (total_post.length === 2) {
                        // Here written logic for alternative posting. 
                        // will do altenrative posting till the lowest length of the posts 
                        if (total_post[0].posts.length <= total_post[1].posts.length) {
                          var first_mem_data = total_post[0]
                          var sec_mem_data = total_post[1]
                        }else{
                          var first_mem_data = total_post[1]
                          var sec_mem_data = total_post[0]
                        }
                        for (var i = 0; i < first_mem_data.posts.length ; i++) {
                            var first_per = {
                                user : first_mem_data.user,
                                posts : []
                                };
                            first_per.posts.push(first_mem_data.posts[i]);
                            var final_posts_data = post_template_data(first_per,options)
                            $('.render_feed').append(final_posts_data);
                            var second_per = {
                                user : total_post[1].user,
                                posts : []
                                };
                            second_per.posts.push(sec_mem_data.posts[i]);
                            var final_posts_data = post_template_data(second_per,options)
                            $('.render_feed').append(final_posts_data);
                          }
                        for (var i = first_mem_data.posts.length; i < sec_mem_data.posts.length ; i++) {
                          var remain_posts = {
                              user : sec_mem_data.user,
                              posts : []
                              };
                          remain_posts.posts.push(sec_mem_data.posts[i]);
                          var final_posts_data = post_template_data(remain_posts,options)
                          $('.render_feed').append(final_posts_data);
                        }
                      }
                    }
                });
                return this;
            };
        render_wall(graphUSER,graphPOSTS);
    }

    function post_template_data(all_posts,options){
        var posts_str = "<% _.forEach(fb_glob.posts,function(u,i){  %>"+
                           "<a href='/engage/' target='_blank'> <div class='row standard_row' style='padding:0px 20px;'> "+
                           "          <div class='col-sm-2' style='padding-top:2.5%' > "+
                           "             <img src='<%= fb_glob.user.picture.data.url %>' class='img img-responsive img-circle' style='position:relative;height:50px;width:50px;'> "+
                           "         </div> "+
                           "         <div class='col-sm-10'> "+
                           "             <h5 style='padding-left:0px;'><%= fb_glob.user.name %></h5> "+
                           "             <p style='font-size:12px;color:#d1cfcf;line-height:4px;'><%= u.created_time %>&nbsp <i class='fa fa-briefcase' aria-hidden='true'></i></p> "+
                           "         </div>"+
                           "     </div> "+
                           "     <div class='row'> "+
                           "         <div class='col-sm-offset-1 col-sm-11' style='max-height:68px;overflow-y:auto;'> "+
                           "             <p style='font-size:12px;'><%= u.message %></p>"+
                           "         </div> "+
                           "         <div class='row standard_row' style='width:80%;float:right;'> "+
                           "             <p style='float:right;font-size:12px;color:#888'><%= u.story %>.</p> "+
                           "         </div>"+
                           "<div class='row standard_row' style='text-align:center;'>"+
                           "         <hr style='width:92%;margin-left:8%;' >"+
                           "</div>"+
                           "     </div> </a>"+
                           "<% }) %>";
        template_str = (typeof options.template === 'undefined' || !options.template) ? posts_str : options.template
        fb_glob = all_posts
        var post_template = _.template( template_str );
        post_template( fb_glob );
        return post_template
        }

        // Helper functions:

    function urlHyperlinks(str){
        return str.replace(/\b((http|https):\/\/\S+)/g,'<a href="$1" target="_blank">$1</a>');
    }

    function relativeTime(time){

        // Adapted from James Herdman's http://bit.ly/e5Jnxe

        var period = new Date(time);
        var delta = new Date() - period;

        if (delta <= 10000) {   // Less than 10 seconds ago
            return 'Just now';
        }

        var units = null;

        var conversions = {
            millisecond: 1,     // ms -> ms
            second: 1000,       // ms -> sec
            minute: 60,         // sec -> min
            hour: 60,           // min -> hour
            day: 24,            // hour -> day
            month: 30,          // day -> month (roughly)
            year: 12            // month -> year
        };

        for (var key in conversions) {
            if (delta < conversions[key]) {
                break;
            }
            else {
                units = key;
                delta = delta / conversions[key];
            }
        }

        // Pluralize if necessary:

        delta = Math.floor(delta);
        if (delta !== 1) { units += 's'; }
        return [delta, units, "ago"].join(' ');

    }
    })(jQuery);

