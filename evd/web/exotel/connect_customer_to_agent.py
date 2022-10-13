#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import requests

from settings import sid, token


def connect_customer_to_agent(sid, token,
                              agent_no, customer_no, callerid,
                              timelimit=None, timeout=None, calltype='trans'):
    return requests.post('https://twilix.exotel.in/v1/Accounts/{sid}/Calls/connect.json'.format(sid=sid),
        auth=(sid, token),
        data= {
            'From': agent_no,
            'To': customer_no,
            'CallerId': callerid,
            'TimeLimit': timelimit,
            'TimeOut': timeout,
            'CallType': calltype
        })


if __name__ == '__main__':
    r = connect_customer_to_agent(
        sid, token,
        agent_no="08039591606",
        customer_no="",
        callerid="08039591606",
        timelimit="<time-in-seconds>",  # This is optional
        timeout="<time-in-seconds>",  # This is also optional
        calltype="trans"  # Can be "trans" for transactional and "promo" for promotional content
        )
    print r.status_code
    pprint(r.json())
