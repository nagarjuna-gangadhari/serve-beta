$("document").ready(
    function(){
	$(".simple-tree").toggle(
    	    function(){
	        $(this).next("ul").show();      
    	    },
    	    function(){
		$(this).next("ul").hide();
    	    }
	)
    }
);

