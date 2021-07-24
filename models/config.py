import json
import os
import logging

log = logging.getLogger()
config_path = os.path.join('../', os.curdir, 'config.json')

class Config:
    """The configuration file for the bot. Contains sensitive credentials, i.e. tokens and API keys."""

    token = ''
    prefix = '/'
    owner_ids = []
    postgres_db = ''
    postgres_user = ''
    postgres_password = ''
    postgres_host = ''
    postgres_port = ''

    def __init__(self):
        if os.path.exists(config_path):
            with open(config_path) as cfg_file:
                try:
                    data = json.load(cfg_file)
                    self.token = data['token']
                    self.prefix = data['prefix']
                    self.owner_ids = data['owner_ids']
                    self.postgres_db = data['postgres_db']
                    self.postgres_user = data['postgres_user']
                    self.postgres_password = data['postgres_password']
                    self.postgres_host = data['postgres_host']
                    self.postgres_port = data['postgres_port']
                except TypeError:
                    log.error('File at {} is corrupted or empty.'.format(config_path))
                    self.save_config()
        else:
            self.save_config()  # Saves default config

    def save_config(self):
        """Saves configuration to a JSON file"""

        with open(config_path, 'w') as cfg_file:
            json.dump(self.json_data(), cfg_file, indent=True)

    def json_data(self):
        return {
            'token': self.token,
            'prefix': self.prefix,
            'owner_ids': self.owner_ids
        }
