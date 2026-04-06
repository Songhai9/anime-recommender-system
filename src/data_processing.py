import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys


logger = get_logger(__name__)

class DataProcessor:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.X_train_array = None
        self.X_test_array = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.user2user_decoded = {}
        self.anime2anime_encoded = {}
        self.anime2anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info('Data processing started')

    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)
            logger.info('Data loaded successfully for data processing')
        except Exception as e:
            raise CustomException(f'Failed to load data', sys)
        
    def filter_user(self, min_rating=400):
        try:
            n_ratings = self.rating_df['user_id'].value_counts()
            self.rating_df = self.rating_df[self.rating_df['user_id'].isin(n_ratings[n_ratings >= 400].index)].copy()
            logger.info('Filtered users successfully')
        except Exception as e:
            raise CustomException(f'Failed to filter data', sys)
        
    def scale_ratings(self):
        try:
            min_rating = min(self.rating_df['rating'])
            max_rating = max(self.rating_df['rating'])
            self.rating_df['rating'] = self.rating_df['rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values.astype('float')
            logger.info('Scaling done for processing successfully')
        except Exception as e:
            raise CustomException(f'Failed to scale data', sys)
        
    def encode_data(self):
        try:
            ### Users
            user_ids = self.rating_df['user_id'].unique().tolist()
            self.user2user_encoded = {x: i for i, x in enumerate(user_ids)}
            self.user2user_decoded = {i: x for i, x in enumerate(user_ids)}
            self.rating_df['user'] = self.rating_df['user_id'].map(self.user2user_encoded)

            ### Animes
            anime_ids = self.rating_df['anime_id'].unique().tolist()
            self.anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i: x for i, x in enumerate(anime_ids)}
            self.rating_df['anime'] = self.rating_df['anime_id'].map(self.anime2anime_encoded)

            logger.info('Encoding done for users and animes')
        except Exception as e:
            raise CustomException(f'Failed to encode data', sys)
    
    def split_data(self, test_size=1000, random_state=9):
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=9).reset_index(drop=True)

            X = self.rating_df[['user', 'anime']].values
            y = self.rating_df['rating']

            train_indices = self.rating_df.shape[0] - test_size

            X_train, X_test, y_train, y_test = (
                X[:train_indices],
                X[train_indices:],
                y[:train_indices],
                y[train_indices:]
            )

            X_train_array = [X_train[:, 0], X_train[:, 1]]
            X_test_array = [X_test[:, 0], X_test[:, 1]]
            self.y_train_array = y_train
            self.y_test_array = y_test

            logger.info('Data splitted successfully')
        except Exception as e:
            raise CustomException(f'Failed to split data', sys)
    

    def save_artifacts(self):
        try:
            artifacts = {
                'user2user_encoded': self.user2user_encoded,
                'user2user_decoded': self.user2user_decoded,
                'anime2anime_encoded': self.anime2anime_encoded,
                'anime2anime_decoded': self.anime2anime_decoded
            }

            for name, data in artifacts.items():
                joblib.dump(
                    data,
                    os.path.join(self.output_dir, f'{name}.pkl')
                )

                logger.info(f'{name} saved successfully in processed directory')
            
            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train_array, Y_TRAIN_ARRAY)
            joblib.dump(self.y_test_array, X_TEST_ARRAY)

            self.rating_df.to_csv(RATING_DF, index=False)

            logger.info('Save data successfully')
        except Exception as e:
            raise CustomException(f'Failed to save data', sys)
        
    def process_anime_data(self):
        try:
            df = pd.read_csv(ANIME_CSV)
            cols = ['MAL_ID', 'Name', 'Genres', 'sypnopsis']
            synopsis_df = pd.read_csv(ANIMESYNOPSIS_CSV, usecols=cols)

            df = df.replace('Unknown', np.nan)

            def getAnimeName(anime_id):
                try:
                    name = df[df['anime_id'] == anime_id]['eng_version'].values[0]
                    if name is np.nan:
                        name = df[df['anime_id'] == anime_id]['Name'].values[0]
                except:
                    print('Error')
                return name
            
            df['anime_id'] = df['MAL_ID']
            df['eng_version'] = df['English name']
            df['eng_version'] = df['anime_id'].apply(lambda x: getAnimeName(x))

            df.sort_values(
                by=['Score'],
                ascending=False,
                kind='quicksort',
                na_position='last',
                inplace=True
            )

            df = df[['anime_id', 'eng_version', 'Score', 'Genres', 'Episodes', 'Type', 'Premiered', 'Members']]

            df.to_csv(DF_PATH, index=False)
            synopsis_df.to_csv(SYNOPSIS_DF, index=False)

            logger.info('DF and SYNOPSIS_DF saved successfully')
        except Exception as e:
            raise CustomException(f'Failed to save CSVs', sys)
    

    def run(self):
        try:
            self.load_data(usecols=['user_id', 'anime_id', 'rating'])
            self.filter_user()
            self.encode_data()
            self.split_data()
            self.save_artifacts()

            self.process_anime_data()

            logger.info('Data processing pipeline run successfully')
        except CustomException as e:
            logger.error(str(e))


if __name__ == '__main__':
    data_proceccsor = DataProcessor(ANIMELIST_CSV, PROCESSED_DIR)
    data_proceccsor.run()
    
        
