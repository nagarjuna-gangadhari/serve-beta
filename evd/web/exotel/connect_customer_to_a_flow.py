#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import requests

from settings import sid, token


def connect_customer(sid, token,
                     customer_no, exotel_no, callerid, url,
                     timelimit=None, timeout=None, calltype="trans",
                     callback_url=None):
    return requests.post('https://twilix.exotel.in/v1/Accounts/{sid}/Calls/connect.json'.format(sid=sid),
        auth=(sid, token),
        data={
            'From': customer_no,
            'To': exotel_no,
            'CallerId': callerid,
            'Url': url,
            'TimeLimit': timelimit,
            'TimeOut': timeout,
            'CallType': calltype,
            'StatusCallback': callback_url
        })


if __name__ == '__main__':
    r = connect_customer(
        sid, token,
        customer_no="<Your-Customer's-Number>",
        exotel_no="<Your-Exotel-Landline-or-Mobile>",
        callerid="<Your-Exotel-virtual-number>",
        url="http://my.exotel.in/exoml/start/123132",
        timelimit="<time-in-seconds>",  # This is optional
        timeout="<time-in-seconds>",  # This is also optional
        calltype="trans",  # Can be "trans" for transactional and "promo" for promotional content
        callback_url="<http//: your company URL>"  # This is also also optional
        )
    print r.status_code
    pprint(r.json())
