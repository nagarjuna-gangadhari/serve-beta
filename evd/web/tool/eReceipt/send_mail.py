#!/usr/bin/env python

import sys
import os
import smtplib
import logging
import traceback
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

SUBJECT     = "Electronic Receipt for your online contribution to eVidyaloka"
SENDER      = "praneeth1249@evidyaloka.org"
PASSWORD    = "070706907"
CC          = ['praneeth1249@gmail.com']
BCC         = []
SERVER      = "smtp.gmail.com"

def init_logger():
    """ Creating Logger for the views """

    log = logging.getLogger('logs/send_mail.log')
    hdlr = logging.FileHandler('logs/send_mail.log')
    formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%dT%H%M%S")
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

    return log

log = init_logger()

def get_msg_body():
    text = """Hello,

THANK YOU for your contribution to eVidyaloka .

The receipt with 80G details and our PAN No. is enclosed., which is good enough for tax purposes.

Do keep a track of our updates on https://www.facebook.com/eVidyaloka


With best regards,
Team eVidyaloka.."""

    return text

def send_mail(to, files=[]):
    log.info("From: %s - To: %s - Files: %s - CC: %s", SENDER, to, files, CC)

    assert type(to)==list
    assert type(files)==list
    assert type(CC)==list
    assert type(BCC)==list

    message = MIMEMultipart()
    message['From'] = SENDER
    message['To'] = COMMASPACE.join(to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = SUBJECT
    message['Cc'] = COMMASPACE.join(CC)
    message.attach(MIMEText(get_msg_body()))

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)

    addresses = []
    for x in to:
        addresses.append(x)
    for x in CC:
        addresses.append(x)
    for x in BCC:
        addresses.append(x)

    try:        
        smtp = smtplib.SMTP(SERVER, 587)
        smtp.starttls()
        smtp.login(SENDER, PASSWORD)
        smtp.sendmail(SENDER, addresses, message.as_string())
        log.info("Mail Sent Successfully to: %s", to)
        smtp.close()
        
        return 1

    except Exception as e:
        log.error("Unable to Send Mail to: %s", to)
        log.error("Error: %s", traceback.format_exc())

        return 0
