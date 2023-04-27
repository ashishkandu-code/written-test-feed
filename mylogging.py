import logging
import logging.config
import yaml
from typing import Final
import os

DEFAULT_LEVEL: Final = logging.INFO


def log_setup(log_cfg_path='cfg.yaml'):
    if os.path.exists(log_cfg_path):
        with open(log_cfg_path, 'rt') as cfg_file:
            try:
                config = yaml.safe_load(cfg_file.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print('Error with file, using Default logging')
                logging.basicConfig(level=DEFAULT_LEVEL)
    else:
        logging.basicConfig(level=DEFAULT_LEVEL)
        print('Config file not found, using Default logging')
   