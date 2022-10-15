;(function () {

    var evl = window.EVL = window.EVL || {},
        user_location_info = evl.user_location_info;


    function ajaxCall() {
        this.send = function(data, url, method, success, type) {
          type = type||'json';
          var successRes = function(data) {
              success(data);
          }

          var errorRes = function(e) {
              console.log(e);
//              alert("Error found \nError Code: "+e.status+" \nError Message: "+e.statusText);
              $('#loader').modal('hide');
          }
            return $.ajax({
                url: '/get_location_data/',
                type: method,
                data: data,
                success: successRes,
                error: errorRes,
                dataType: type,
                timeout: 60000
            });

          }

        }

    var countriesResp, selectedCountryId, statesResp, selectedStateId, citiesResp, selectedCityId;

    function locationInfo() {
        var rootUrl = "http://lab.iamrohit.in/php_ajax_country_state_city_dropdown/apiv1.php";
        var call = new ajaxCall();
        this.getCities = function(id, selectedCity) {
            $(".cities option:gt(0)").remove();
            var url = rootUrl+'?type=getCities&stateId=' + id;
            $('.cities').find("option:eq(0)").html("Please wait..");
            citiesResp = $.getJSON('/get_location_data/', {'url' : url}, function(data) {
                $('.cities').find("option:eq(0)").html("Select City");
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                        option.attr('value', val).text(val);
                         option.attr('cityid', key);
                         if (selectedCity && (selectedCity.toLowerCase() == val.toLowerCase())){
                            selectedCityId = key;
                            option.attr('selected', 'selected');
                         }
                        $('.cities').append(option);
                    });
                    $(".cities").prop("disabled",false);
                    $('.cities').append('<option val="others">Others</option>');
                }
                else{
                     alert(data.msg);
                }
            });
            return citiesResp
        };

        this.getStates = function(id, selectedState) {
            $(".states option:gt(0)").remove();
            $(".cities option:gt(0)").remove();
            var url = rootUrl+'?type=getStates&countryId=' + id;
            $('.states').find("option:eq(0)").html("Please wait..");
            statesResp = $.getJSON('/get_location_data/', {'url' : url}, function(data) {
                $('.states').find("option:eq(0)").html("Select State");
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                            option.attr('value', val).text(val);
                            option.attr('stateid', key);
                            if (selectedState && (selectedState.toLowerCase() == val.toLowerCase())){
                                selectedStateId = key;
                                option.attr('selected', 'selected');
                            }
                        $('.states').append(option);
                    });
                    $(".states").prop("disabled",false);
                    if($('.states').children().length == 1){
                        $('.states').append('<option val="others">Others</option>');
                        $('.cities').append('<option val="others">Others</option>');
                    }
                }
                else{
                    alert(data.msg);
                }
            });
            return statesResp
        };

        this.getCountries = function(selectedCountry) {

            if (countriesResp) {

              return countriesResp
            }

            var url = rootUrl+'?type=getCountries';
            //$('.countries').find("option:eq(0)").html("Please wait..");
            countriesResp = $.getJSON('/get_location_data/', {'url' : url}, function(data) {
                //$('.countries').find("option:eq(0)").html(current_country);
               // console.log(data);
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                        option.attr('value', val).text(val);
                        option.attr('countryid', key);
                        if (selectedCountry && (selectedCountry.toLowerCase() == val.toLowerCase())){
                            selectedCountryId = key;
                            option.attr('selected', 'selected');
                        }
                        $('.countries').append(option);
                    });
                    $(".countries").prop("disabled",false);
                }
                else{
                    alert(data.msg);
                }
            });

            return countriesResp;
        };

    }

    $(function() {
        var loc = new locationInfo();
        var countriesResp = loc.getCountries(user_location_info.country);

        if (user_location_info.state) {

          $.when(countriesResp).done(function () {

            statesResp = loc.getStates(selectedCountryId, user_location_info.state);
            if (user_location_info.city) {

                $.when(statesResp).done(function () {

                    citiesResp = loc.getCities(selectedStateId, user_location_info.city);
                });
            }

          });
        }

        $(".countries").on("change", function(ev) {
            var countryId = $("option:selected", this).attr('countryid');
            if(countryId != ''){
            loc.getStates(countryId);
            }
            else{
                $(".states option:gt(0)").remove();
            }
        });
        $(".states").on("change", function(ev) {
            var stateId = $("option:selected", this).attr('stateid');
            if(stateId != ''){
            loc.getCities(stateId);
            }
            else{
                $(".cities option:gt(0)").remove();
            }
        });
    });

}());
