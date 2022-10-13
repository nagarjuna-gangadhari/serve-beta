import logging
import os


LOG_DIR = os.path.abspath(os.path.dirname(__file__))

def init_logger(fname):
    """ Creating Logger for the views """
    if not fname.endswith('.log'):
        fname = "{}.log".format(fname)

    log_file = os.path.join(LOG_DIR, fname)
    log = logging.getLogger(log_file)
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%dT%H%M%S")
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

    return log
