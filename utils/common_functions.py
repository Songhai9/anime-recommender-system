import os
import pandas as pd

from src.logger import get_logger
from src.custom_exception import CustomException
import yaml
import sys

logger = get_logger(__name__)

def read_yaml(filepath):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'File is not in the given path')
        with open(filepath, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info('Successfully read the YAML file')
            return config
    except Exception as e:
        logger.error('Error while reading YAML file')
        raise CustomException('Failed to read YAML file', e)