import logging
import os
from datetime import datetime
from datetime import date

logs_path = os.path.join('../', 'logs')

def create_logger():
    create_log_folder()

    # File logging
    today = date.today()
    time = datetime.now()
    date_format = '%04d-%02d-%02d' % (today.year, today.month, today.day)
    time_format = time.now().strftime('%H-%M-%S')

    logging.basicConfig(filename='{}/mackerel_{}_{}.log'.format(logs_path, date_format, time_format), filemode='w',
                        level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

    log = logging.getLogger()
    log.setLevel(logging.DEBUG) # Log level for file

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG) # Log level for command line

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    ch.setFormatter(formatter)

    log.addHandler(ch)

def create_log_folder():
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
        print(f'Logs directory not found. Created at {os.path.abspath(logs_path)}')
