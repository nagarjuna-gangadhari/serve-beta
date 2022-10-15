/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload();
    $('#fileupload').fileupload('option', {
        autoUpload:true
    });
    if(!$.support.opacity){
        $('#fileupload').bind('fileuploadadd', function(e, data) {
            debugger;
            $("p.watermark-content").text("Loading...");
        });
    }
    $('#fileupload').bind('fileuploadprogressall', function (e, data) {
       var $progress = $(this).find("span.progress-bar"),
            progress = parseInt(data.loaded / data.total * 100, 10)+"%";
       $progress.removeClass("hide");
       $progress.children("span.bar").css({"width": progress});
       $progress.children("span.perc").text(progress);
       if(!$.support.opacity){
            $("p.watermark-content").text("Loading...");
       }
    });
    $('#fileupload').bind('fileuploaddone', function (e, data) {
        var $progress = $(this).find("span.progress-bar");
        $progress.addClass("hide");
        $progress.children("span.bar").css({"width": "0%"});
        $progress.children("span.perc").text("0%");
        console.log(data.result[0].url);
        $(".profile_pic").attr("src",data.result[0].url);
        $("#photo-upload-modal").modal("hide");
        if(!$.support.opacity){
             $("p.watermark-content").text("Drag and drop to upload photo");
        }
    });
});
