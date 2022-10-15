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
            $(".cities1 option:gt(0)").remove();
            var url = rootUrl+'?type=getCities&stateId=' + id;
            $('.cities1').find("option:eq(0)").html("Please wait..");
            citiesResp = $.getJSON('/get_location_data/', {'url' : url}, function(data) {
                $('.cities1').find("option:eq(0)").html("Select City");
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                        option.attr('value', val).text(val);
                         option.attr('native_city', key);
                         if (selectedCity && (selectedCity.toLowerCase() == val.toLowerCase())){
                            selectedCityId = key;
                            option.attr('selected', 'selected');
                         }
                        $('.cities1').append(option);
                    });
                    $(".cities1").prop("disabled",false);
                    $('.cities1').append('<option val="others">Others</option>');
                }
                else{
                     alert(data.msg);
                }
            });
            return citiesResp
        };

        this.getStates = function(id, selectedState) {
            $(".states1 option:gt(0)").remove();
            $(".cities1 option:gt(0)").remove();
            var url = rootUrl+'?type=getStates&countryId=' + id;
            $('.states1').find("option:eq(0)").html("Please wait..");
            statesResp = $.getJSON('/get_location_data/', {'url' : url}, function(data) {
                $('.states1').find("option:eq(0)").html("Select State");
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                            option.attr('value', val).text(val);
                            option.attr('native_state', key);
                            if (selectedState && (selectedState.toLowerCase() == val.toLowerCase())){
                                selectedStateId = key;
                                option.attr('selected', 'selected');
                            }
                        $('.states1').append(option);
                    });
                    $(".states1").prop("disabled",false);
                    if($('.states1').children().length == 1){
                        $('.states1').append('<option val="others">Others</option>');
                        $('.cities1').append('<option val="others">Others</option>');
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
                //$('.countries').find("option:eq(0)").html(native_country);
               // console.log(data);
                if(data.tp == 1){
                    $.each(data['result'], function(key, val) {
                        var option = $('<option />');
                        option.attr('value', val).text(val);
                        option.attr('native_country', key);
                        if (selectedCountry && (selectedCountry.toLowerCase() == val.toLowerCase())){
                            selectedCountryId = key;
                            option.attr('selected', 'selected');
                        }
                        $('.countries1').append(option);
                    });
                    $(".countries1").prop("disabled",false);
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

        $(".countries1").on("change", function(ev) {
            var countryId = $("option:selected", this).attr('native_country');
            if(countryId != ''){
            loc.getStates(countryId);
            }
            else{
                $(".states1 option:gt(0)").remove();
            }
        });
        $(".states1").on("change", function(ev) {
            var stateId = $("option:selected", this).attr('native_state');
            if(stateId != ''){
            loc.getCities(stateId);
            }
            else{
                $(".cities1 option:gt(0)").remove();
            }
        });
    });

}());
