function autoLoginWikividya(url) {
	$.ajax({
		url : '/v2/ajax/callMedia',
		success : function(data) {
			console.log("data : = "+data);
			if (data != null && data != 'undefined' && data != '' && data.indexOf('session')>-1) {
				var arrayStr = data.split("__");
				var arrayData = arrayStr;
				var token = arrayStr[0];
				arrayStr = arrayStr[1].split("=")[1];
				arrayStr = arrayStr.split(" ")[0];
				$("#csessionId").val(arrayStr);
				$("#lg_token").val(token);
				var username = arrayData[2].split(",")[0];
				var passw = arrayData[2].split(",")[1];
				$("#wiki_lgname").val(username);
				$("#wiki_lgpass").val(passw);
				if (token != null && token != 'undefined' && token != ''){
					setAutoLoginCookies(token, arrayStr, url);
				}else{
					window.open(url, '_blank');
				}
			}else{
				window.open(url, '_blank');
			}
		},
		error : function() {
		}
	});
}

function setAutoLoginCookies(token, sessionId, url) {
	var flag = false;
	deleteAutoLoginCookie(flag, sessionId, false);
	var d = new Date();
	d.setTime(d.getTime() + (1 * 24 * 60 * 60 * 1000));
	var expires = "expires=" + d.toUTCString();
	console.log(sessionId);
	document.cookie = "wiki_1_26_session" + "=" + sessionId + ";" + expires + ";path=/ ; domain=.evidyaloka.org";
	console.log(document.cookie);
	if (deleteAutoLoginCookie(flag, sessionId, true)){
		localStorage.setItem('token',token);
		localStorage.setItem('sessionId',sessionId);
	}else{
		$("#csessionId").val(localStorage.getItem('sessionId'));
		$("#lg_token").val(localStorage.getItem('token'));
	}
	document.getElementById("formMedia").submit();
	
	
	var a = document.createElement('a');
//	url = 'http://wikividyadev.evidyaloka.org';
//	url = 'http://106.51.126.221/';
	a.href = url;
	a.target = '_blank';
	document.body.appendChild(a);
	a.click();
	
}

function deleteAutoLoginCookie(flag, sessionId, createFlag){
	var cookiearray = document.cookie.split(';');
//	console.log("delete"+cookiearray);
	for (var i = 0; i < cookiearray.length; ++i) {
		if (cookiearray[i].trim().indexOf('wiki_1_26_session=') > -1) {
			if (!createFlag){
				document.cookie = "wiki_1_26_session" + "=" + sessionId + ";expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
			}
			flag = true
		}
	}
	return flag;
}