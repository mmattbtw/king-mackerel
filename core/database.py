import psycopg2
import logging
from sqlalchemy import create_engine
from models.config import Config

log = logging.getLogger()
cfg = Config()

# Setup connection to postgres server

def get_database():
    try:
        engine = get_engine()
        log.info("Connected to PostgreSQL database!")
    except IOError:
        log.exception("Failed to get database connection!")
        return None

    return engine

def get_engine():
    url = f'postgresql://{cfg.postgres_user}:{cfg.postgres_password}@{cfg.postgres_host}:{cfg.postgres_port}/{cfg.postgres_db}'
    engine = create_engine(url)
    return engine

