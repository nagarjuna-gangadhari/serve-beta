import sys
import requests

def test_post_request():

    with requests.Session() as s:
        print s.cookies
        csrf_response = s.get('http://dev.evidyaloka.org:9090/rest_authentication/csrf')

        print csrf_response.cookies
        print s.cookies

        payload = {"csrfmiddlewaretoken": s.cookies['csrftoken']}
        demand_response = s.post('http://dev.evidyaloka.org:9090/get_demand/', data=payload)
        import pdb; pdb.set_trace()
        print demand_response

        #payload = {"username": "admin2", "password": "admin2", "csrfmiddlewaretoken": s.cookies['csrftoken']}
        #headers = {"Cookie": ";".join("{}={}".format(k,v) for k,v in s.cookies.iteritems())}
        #headers = {"Cookie": "X-CSRFToken={}".format(s.cookies['csrftoken'])}
        #print headers
        #login_response = s.post('http://dev.evidyaloka.org:9090/rest_authentication/login/', data=payload)
        #print login_response.text


def test_post():
    resp = requests.get('http://dev.evidyaloka.org:9090/rest_authentication/csrf')
    print "Ensure Csrf response Csrftoke: {}".format(resp.cookies)

    csrftoken = resp.cookies['csrftoken']
    headers = {"Cookie": ";".join("{}={}".format(k,v) for k,v in resp.cookies.iteritems())}
    print "Headers before Login: {}".format(headers)
    default_payload = {"csrfmiddlewaretoken": csrftoken}
    demand_response = requests.post('http://dev.evidyaloka.org:9090/get_demand/', data=default_payload, headers=headers)
    print "Demands Response: {}".format(demand_response.status_code)

    payload = {"username": "admin2", "password": "admin2", "csrfmiddlewaretoken": csrftoken}
    login_response = requests.post('http://dev.evidyaloka.org:9090/rest_authentication/login/', data=payload, headers=headers)
    print "Login Response: {}".format(login_response.status_code)
    if not login_response.status_code == 200:
        sys.exit()

    sessionid = login_response.cookies['sessionid']
    headers['Cookie'] = ";".join([headers['Cookie'], 'sessionid={}'.format(sessionid)])
    print "Headers After Login: {}".format(headers)

    rel_response = requests.post('http://dev.evidyaloka.org:9090/release_demand/', data=default_payload, headers=headers)
    print "Release Response: {}".format(rel_response.status_code)

    logout_response = requests.post('http://dev.evidyaloka.org:9090/rest_authentication/logout/', data=default_payload, headers=headers)
    print "Logout Response: {}".format(logout_response.status_code)

    rel_response = requests.post('http://dev.evidyaloka.org:9090/release_demand/', data=default_payload, headers=headers)
    print "Afterlogout Release Response: {}".format(rel_response.status_code)
test_post()
