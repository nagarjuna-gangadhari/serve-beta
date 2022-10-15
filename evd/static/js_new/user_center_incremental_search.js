//text_box_id = Give text box class_name or id with . or #  
function getUsersByRole(text_box_id, role_id, user_type) {
	var ajax_url = '/v2/ajax/getSelUsers?role_id=' + role_id + '&type='+ user_type;
	$(text_box_id).autocomplete({
		source : ajax_url,
		minLength : 1,
		select : function(event, ui) {
			$(text_box_id + '_val').val(ui.item.id);
		},
		change : function(event, ui) {
			if (ui.item) {
				return;
			} else {
				$(this).val('');
				$(text_box_id + '_val').val('');
			}
		}
	});
}

function getCenters(search_results, gotocenterID) {

	$(search_results).autocomplete(
					{
						source : "/v2/ajax/getSelCentersBaseOnUser",
						minLength : 1,
						autoFocus : true,
						select : function(event, ui) {

							  $(this).val(ui.item.value);

							 $('#gotocenterID').click(function() {

							       var center = document.getElementById('search_results').value;

								   if (center == ui.item.value) {

							            window.location = '/centeradmin/?center_id='+ ui.item.id+ '&ay_id='+ ui.item.ay;

									  } 

								});

						},

						change : function(event, ui) {

							if (ui.item) {
								return;
							} else {
								$(this).val('');
								
							}
						}
					});
}


function getCentersForPartner(search_results, gotocenterID){
	$(search_results).autocomplete(
			{
				source : "/v2/ajax/getCentersForPartner",
				minLength : 1,
				autoFocus : true,
				select : function(event, ui) {

					  $(this).val(ui.item.value);

					 $('#gotocenterID').click(function() {

					       var center = document.getElementById('search_results').value;

						   if (center == ui.item.value) {

					            window.location = '/centeradmin/?center_id='+ ui.item.id+ '&ay_id='+ ui.item.ay;

							  } 

						});

				},

				change : function(event, ui) {

					if (ui.item) {
						return;
					} else {
						$(this).val('');
						
					}
				}
			});
	
}


function getExternalRoleVolunteer(search_results){
	var center_id = parent.window.center_id;
	$(search_results).autocomplete(
	{
	source : "/v2/ajax/getExternalRoleVolunteer?center_id="+center_id,
	minLength : 1,
	autoFocus : true,
	select : function(event, ui) {

	 $(this).val(ui.item.value);
	},

	change : function(event, ui) {
	if (ui.item) {
	return;
	} else {
	$(this).val('');

	}
	}
	});
	}

	function getMouPartner(search_results){
        $(search_results).autocomplete(
        {
			source : "/partner/ajax/get_mou_partner",
			minLength : 1,
			autoFocus : true,
			select : function(event, ui) {
				$(this).val(ui.item.value);
        },
    
        change : function(event, ui) {
			if (ui.item) {
				return;
			} else {
				$(this).val('');
			}
		}
	}
	);
}