$(document).ready(function(){

Dropzone.options.myAwesomeDropzone = {
                    url: "/save_profilepic/",
                    method : 'post',
                    parallelUploads : 1,
                    maxFiles: 1,
                    dictDefaultMessage : 'Drop/Click here to upload a picture.',
                    maxFilesize  : 1,
                    autoProcessQueue : false,
                    uploadMultiple : false,
                    acceptedFiles  : 'image/*',
                    clickable: ['.dz-click', '.dropzone'],
                    maxFiles : 1,
                    init: function() {
                      var that = this;
                      this.on("error", function(file, message) {
                                    this.removeFile(file);
                                    $('#profile_pic_warn').removeClass('hidden').find('p').text(message);
                      });
                      this.on("maxfilesexceeded", function(file){
                                   this.removeFile(file);
                                   $('#profile_pic_warn').removeClass('hidden').find('p').text('Only one file is allowed. Clear to upload another.');
                      });
                      document.querySelector(".dz-start").onclick = function() {
                          //that.enqueueFiles(that.getFilesWithStatus(Dropzone.ADDED));
                                   that.enqueueFiles(that.processQueue());
                      };
                      document.querySelector(".dz-remove").onclick = function() {
                                   $('#profile_pic_warn').addClass('hidden')
                                   that.removeAllFiles(true);
                      };
                      this.on('success', function( file,resp ){
                                  $('#profile_pic_warn').removeClass('hidden ').find('p').text('Profile pic changed successfully..');
                                  setTimeout(function(){
                                        window.location.reload();
                                  },1500);
                        });
                  },
                 };

$('#change_pic').find('.close').click(function(){
        window.location.reload()
});









}); // Document ready close
