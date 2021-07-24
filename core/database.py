import logging

from peewee import *
from playhouse import postgres_ext
from models.config import Config

log = logging.getLogger()
cfg = Config()

# Setup connection to postgres server

db = postgres_ext.PostgresqlDatabase(cfg.postgres_db, user=cfg.postgres_user, password=cfg.postgres_password, host=cfg.postgres_host)

def connect():
    try:
        db.connect()
        log.info('Connected to database.')
    except Exception as e:
        log.critical('Failed to connect to database! ' + str(e))

def disconnect():
    try:
        db.close()
        log.info('Disconnected from database.')
    except Exception as e:
        log.critical('Failed to disconnect from database! ' + str(e))