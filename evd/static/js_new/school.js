$(document).ready(function(){
    $('#school-signup').click(function(e){
        e.preventDefault();
        var data_serial = $('#school-signup-trigger').serializeArray();
        $.ajax({
            url:"/partner/add_schools/",
            method:"POST",
            data : data_serial,
            success:function(resp) {
                if(resp.status) {
                    alert(resp.message);
                } else {
                    alert(resp);
                }
            }
        });
    });

});
