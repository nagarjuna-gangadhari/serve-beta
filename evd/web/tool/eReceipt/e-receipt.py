#!/usr/bin/env python

import os
import sys
import time
import xlrd
import datetime
import logging
import optparse
import traceback
from glob import glob
from xlrd import open_workbook
from termcolor import colored, cprint       # sudo pip install termcolor

import unicodedata
from htmls import *
from num2word import to_card



P_DIR = os.path.join(os.getcwd(), "web/tool/eReceipt/Process_Excels")
_P_DIR = os.path.join(os.getcwd(), "web/tool/eReceipt/Processed_Excels")
PDFS_DIR = os.path.join(os.getcwd(), "static/uploads/donation_receipts/pdf_files")
FINAL_PDF_FILES = os.path.join(os.getcwd(), "static/uploads/donation_receipts/final_pdf_files")




def init_logger():
    """ Creating Logger for the views """

    log = logging.getLogger('logs/e-receipt.log')
    hdlr = logging.FileHandler('logs/e-receipt.log')
    formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%dT%H%M%S")
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

    return log

def is_xls_file_exist(xls_file):
    file_path = os.path.join(os.getcwd(), "web/tool/eReceipt/Process_Excels/%s" % xls_file)
    print file_path

    return os.path.exists(file_path)

def make_html_file(billno, name, address, amount, date):
    date=date.strftime('%d-%m-%Y')
    num_to_word = to_card(int(str(int(amount)))).replace('-', ' ').replace(',', '').capitalize()

    data = make_single_html_page(billno, name, address, amount, date, num_to_word)

    file_name = "%s_donation.html" % (name.strip().replace(' ', '_'))
    fp = open(file_name, 'w')
    fp.write(data)
    fp.flush()
    fp.close()

    return file_name

class eReceipt:

    def __init__(self):
        self.make_dirs_if_not_exist()

    def make_dirs_if_not_exist(self):
        _dirs = ['logs', 'pdf_files', 'failed_recs', 'final_pdf_files']

        for _dir in _dirs:
            dir_path = os.path.join(os.getcwd(), _dir)
            print dir_path
            if not os.path.exists(dir_path): os.mkdir(_dir)

        if os.path.isdir(dir_path): pass

    def validate_row(self, ws, wb, cur_row):
        name, dt, amount, mail_id, address, billno = '', '', '', '', '', ''

        name    = ws.cell_value(cur_row, 2)
        amount  = ws.cell_value(cur_row, 10)
        mail_id = ws.cell_value(cur_row, 4)
        address = ws.cell_value(cur_row, 15)
        billno  = int(ws.cell_value(cur_row, 1))
        date    = ws.cell_value(cur_row, 24)

        if name and name != "Cardholder Name": name = name
        if amount and amount != "DOMESTIC AMT": amount = amount
        if mail_id and mail_id != "Email-Id": mail_id = mail_id.strip()
        if address and address != "Address": address = str(int(address)) if isinstance(address, float) else address
        if billno and billno != "Bill No": billno = billno

        try:
            if date and date != "Date": dt = datetime.datetime(*xlrd.xldate_as_tuple(date, wb.datemode)).date()
        except Exception:
            log.error("Error: %s", traceback.format_exc())
            cprint("Date Must be DD/MM/YYYY Format...!!", "red")
            sys.exit(1)

        if name and amount and mail_id and address and '@' in mail_id:
            return 1, [name, amount, mail_id, address, billno, dt]
        else:
            return 0, ''

    def get_workbooks(self, xls_file):
        wb = open_workbook(xls_file)
        worksheets = wb.sheet_names()

        return wb, worksheets

    def generate_pdf_file(self, html_file_name, name,bil):
        pdf_file_name = "%s_%s_donation_receipt.pdf" % ( name.strip().replace(' ', '_'), bil)
        cmd = "wkhtmltopdf  -s A4 -L 2mm -R 2mm -B 0mm -T 0mm --minimum-font-size 18  %s %s" % (html_file_name, pdf_file_name)
        os.system(cmd)

        os.system('rm -rf %s' % html_file_name)

        return pdf_file_name

    def move_files(self, _path, _file):
        os.system('mv %s %s' % (_file, _path))

def write_failed_recs_info_file(failed_recs, xls_file):
    f_name="%s_file_failed_records.txt" % xls_file.replace('.', '_')
    cprint("\nFailed Records File: %s" % f_name, "red")
    try:
        with open("failed_recs/%s" % f_name, 'w') as f:
            f.write("Bill No    -  Mail Id\n")
            for f_rec in failed_recs:
                f.write(f_rec)

    except Exception:
        log.error("Error: %s", traceback.format_exc())

def make_mul_recs_in_single_pdf(valid_recs, e, excel_name):
    recs = [valid_recs[i:i+3] for i in range(0, len(valid_recs), 3)]
    today = datetime.datetime.now()
    apnd =  str(today.day)+str(today.month)+str(today.year)
    cprint("##### Started to Generate Multiple Receipts in One Pdf.... #####", "green")
    _pdf_files = []
    for i, rec in enumerate(recs):
        data = """<html><body style="padding: 15px 15px;">%s</body></html>"""

        _html = ''        
        for j, r in enumerate(rec):
            name, amount, email_id, address, billno, date = r

            date=date.strftime('%d-%m-%Y')
            num_to_word = to_card(int(str(int(amount)))).replace('-', ' ').replace(',', '').capitalize()

            _div = """<div style="position: relative;">%s</div>""" if j == 0 else """<div style="position: relative; margin-top: 30px;">%s</div>"""
            _data = adjust_html_to_multiple_receipts(billno, name, address, amount, date, num_to_word)
            _html += _div % _data

        data = data % _html
        
        file_name = "%s_donation.html" % str(i)        
        fp = open(file_name, 'w')
        fp.write(data)
        fp.flush()
        fp.close()

        pdf_file = e.generate_pdf_file(file_name, str(i),apnd)
        _pdf_files.append(pdf_file)

    pdf_files = ' '.join(_pdf_files)
   
    try:
        final_pdf_file = excel_name.replace('.xls', '.pdf')    
        cmd = "pdftk %s cat output %s" % (pdf_files, final_pdf_file)
        os.system(cmd)

        for _pf in _pdf_files: e.move_files(PDFS_DIR, _pf) 
        e.move_files(FINAL_PDF_FILES, final_pdf_file)
        
    except: pass

    return 1

def main(options):
    xls_file        = options.xls_file
    pdf_type    = options.pdf_type

    e = eReceipt()

    global log
    log = init_logger()
    from send_mail import send_mail

    files = [xls_file] if xls_file else glob('%s/*.xls' % P_DIR)
    if not files: print "No Files Found in Process_Excels Directory"; sys.exit(1)

    for f in files:
        print "Processing Started for: ", f.rsplit('/', 1)[-1]

        pass_recs, failed_recs = [], []
        _file = os.path.join(P_DIR, f)

        wb, worksheets = e.get_workbooks(_file)
        for worksheet in worksheets:
            ws = wb.sheet_by_name(worksheet)
            if ws.nrows < 1: break

            valid_recs = []
            for cur_row in range(1, ws.nrows):
                try:
                    is_valid, data = e.validate_row(ws, wb, cur_row)
                    if is_valid:
                        name, amount, mail_id, address, billno, dt = data
                        valid_recs.append([name, amount, mail_id, address, billno, dt])                           

                        if pdf_type == "individual":
                            file_name = make_html_file(billno, name, address, amount, dt)

                            pdf_file = e.generate_pdf_file(file_name, name,str(billno))
                            log.info("Bill No: %s - Name: %s - Mail Id: %s - Pdf File: %s", billno, name, mail_id, pdf_file)
                            _mail = unicodedata.normalize('NFKD', mail_id).encode('ascii','ignore')

                            status = send_mail([_mail], [pdf_file])                        
                            if status:
                                log.info("Mail Sent Successfully to: %s", mail_id)
                                pass_recs.append(_mail)

                            else: failed_recs.append("%s      -   %s\n" % (int(billno), _mail))

                            e.move_files(PDFS_DIR, pdf_file)                    

                except: log.error("Error: %s", traceback.format_exc())

            make_mul_recs_in_single_pdf(valid_recs, e, f.rsplit('/', 1)[-1])

        print "\n############################################"
        print "Total No.of records Passed: ", len(pass_recs)
        print "Total No.of records Failed: ", len(failed_recs)
        print "Process Completed For File: ", f.rsplit('/', 1)[-1]

        if len(failed_recs) > 0: write_failed_recs_info_file(failed_recs, f.rsplit('/', 1)[-1])
        print "#############################################\n"

        e.move_files(_P_DIR, _file)

if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option('-f', '--xls-file', default='', help='XLS File name')
    parser.add_option('-t', '--testing', default='no', help='To Check Created Pdf file content correct / not')
    parser.add_option('', '--pdf-type', default='individual', help='Individual receipt or multiple receipts in one pdf')
    options, args = parser.parse_args()

    if options.xls_file and not is_xls_file_exist(options.xls_file):
        print 'Given XLS file "%s" is not present in the Process_Excels Folder.....\n' % options.xls_file
        sys.exit(1)

    main(options)
