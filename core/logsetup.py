import logging
import os
from datetime import datetime
from datetime import date


def create_logger():
    create_log_folder()

    # File logging
    today = date.today()
    time = datetime.now()
    date_format = '%04d-%02d-%02d' % (today.year, today.month, today.day)
    time_format = time.now().strftime('%H:%M:%S')
    logging.basicConfig(filename='logs/mackerel_{}_{}.log'.format(date_format, time_format), filemode='w',
                        level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

    log = logging.getLogger()
    log.setLevel(logging.DEBUG) # Log level for file

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG) # Log level for command line

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    ch.setFormatter(formatter)

    log.addHandler(ch)

def create_log_folder():
    loc = os.path.join(os.curdir, 'logs')
    if not os.path.isdir(loc):
        log = logging.getLogger()
        os.mkdir(loc)
        log.info('Created new logging directory: {}', loc)
