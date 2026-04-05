import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.file_names = self.config['bucket_file_names']

        os.makedirs(RAW_DIRECTORY, exist_ok=True)
        logger.info('Data ingestion starting')
    
    def download_from_gcp(self):
        try:

            client = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for name in self.file_names:
                file_path = os.path.join(RAW_DIRECTORY, name)

                if name == 'animelist.csv':
                    blob = bucket.blob(name)
                    blob.download_to_filename(file_path)
                    data = pd.read_csv(file_path, nrows=5000000)
                    data.to_csv(file_path, index=False)
                    logger.info('Large file detected, only downloading 5M rows')
                else:
                    blob = bucket.blob(name)
                    blob.download_to_filename(file_path)
                    logger.info('Downloading smaller files')
        except Exception as e:
            logger.error('Error while downloading data from GCP')
            raise CustomException('Failed to download data', e)
    
    def run(self):
        try:
            logger.info('Starting data ingestion process')
            self.download_from_gcp()
            logger.info('Data ingestion completed')
        except CustomException as ce:
            logger.error(f'Custom Exception: {str(ce)}')
        finally:
            logger.info('Data ingestion done')


if __name__ == '__main__':
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()