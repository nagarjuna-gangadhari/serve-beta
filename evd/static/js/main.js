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
    $("#fileupload").fileupload();
    $("#ppupload").fileupload();
    $('#fileupload,#ppupload').fileupload('option', {
            autoUpload: true,
            previewSourceFileTypes: /^image\/(gif|jpeg|png)$/,
            previewMaxWidth: 100,
            previewMaxHeight: 100 
    }); 
    $("#ppupload").bind("fileuploaddone",function(e, data){
        $(this).hide();
        $(this).next("div").append("<img src='"+ data.result[0].url+"'/>");
    }); 
    $("#fileupload").bind('fileuploadadded', function (e, data) {
        var $parent = $(this).parents(".photo-upload-modal");
        if($(window).height() - 50 < $parent.height())
                    $parent.css({"max-height": ($(window).height() - 50) +"px", "overflow-y": "scroll"});
        else
            $parent.css({"max-height": "100%", "overflow-y": "hidden"});

    }); 
});

