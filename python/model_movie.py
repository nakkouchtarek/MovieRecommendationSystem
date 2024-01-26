import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import joblib
import re
import json
import os

# item-based collaborative filtering

class MovieRecommendationEngine:
    def __init__(self, connection, model_file="knn_model.joblib", n_neighbours=20):
        self.movies = pd.DataFrame(connection.item_based_movies.find({}))
        self.ratings = pd.DataFrame(connection.item_based_ratings.find({}))
        self.filename = model_file
        self.knn = None

        # reshape our dataset and replace na values with 0
        self.final_dataset = self.ratings.pivot(index='movieId',columns='userId',values='rating')
        self.final_dataset.fillna(0,inplace=True)

        # count votes per movie and user
        self.votes_per_movie = self.ratings.groupby('movieId')['rating'].agg('count')
        self.votes_per_user = self.ratings.groupby('userId')['rating'].agg('count')

        # remove noise from dataset
        self.final_dataset = self.final_dataset.loc[self.votes_per_movie[self.votes_per_movie > 10].index, :]
        self.final_dataset = self.final_dataset.loc[:, self.votes_per_user[self.votes_per_user > 50].index]

        # reduce sparsity by implementing a sparse matrix
        self.csr_data = csr_matrix(self.final_dataset.values)
        self.final_dataset.reset_index(inplace=True)
        
        # check whether model exists or not so we can load or train new one
        if os.path.isfile(self.filename):   
            self.load_model()
        else:
            self.train_model(n_neighbours)

    def train_model(self, n=20):
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n, n_jobs=-1)
        self.knn.fit(self.csr_data)

        joblib.dump(self.knn, self.filename)

    def load_model(self):
        self.knn = joblib.load(self.filename)

    def test_model(self, distances):
        original_vector = np.array(distances)
        min_value = original_vector.min()
        max_value = original_vector.max()

        normalized_vector = (original_vector - min_value) / (max_value - min_value)
        return np.mean(normalized_vector)
    
    def get_movie_recommendation(self, movie_name, n_movies_to_recommend):
        movie_name = re.sub(r'\([^)]*\)', '', movie_name).strip()
        
        # genres and movies that contains the movie
        try:
            # get movieID inside movies dataframe ( fetch row and get movieId value )
            movie_idx = self.movies[self.movies['title'].str.contains(movie_name)].iloc[0]['movieId']
            # get index of movie inside dataset ( fetch row and get row index )
            movie_idx = self.final_dataset[self.final_dataset['movieId'] == movie_idx].index[0]
            # get distances and indices of all the nodes similar to input ( n+1 cus the node itself counts )
            distances , indices = self.knn.kneighbors(self.csr_data[movie_idx], n_neighbors=n_movies_to_recommend+1)
            # sorted list of tuples containing indices and distances for earlier results, reversed so we have biggest first and remove first elements since its the node itself
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1], reverse=True)[:-1]
            # list to store titles

            rec = []
            i = 0
            for val in rec_movie_indices:
                movie_idx = self.final_dataset.iloc[val[0]]['movieId']
                idx = self.movies[self.movies['movieId'] == movie_idx].index
                # append title and genres
                #rec[i] = {}
                #rec[i]['title'] = self.movies.iloc[idx]['title'].values[0]
                #rec[i]['genres'] = self.movies.iloc[idx]['genres'].values[0].split("|")
                rec.append(self.movies.iloc[idx]['title'].values[0])
                i += 1

            return rec[::-1]
        
        except Exception as e:
            return []
        
    def get_movie_recommendation_with_genre(self, movie_name, n_movies_to_recommend):
        movie_name = re.sub(r'\([^)]*\)', '', movie_name).strip()
        
        # genres and movies that contains the movie
        try:
            # get movieID inside movies dataframe ( fetch row and get movieId value )
            movie_idx = self.movies[self.movies['title'].str.contains(movie_name)].iloc[0]['movieId']
            # get index of movie inside dataset ( fetch row and get row index )
            movie_idx = self.final_dataset[self.final_dataset['movieId'] == movie_idx].index[0]
            # get distances and indices of all the nodes similar to input ( n+1 cus the node itself counts )
            distances , indices = self.knn.kneighbors(self.csr_data[movie_idx], n_neighbors=n_movies_to_recommend+1)
            # sorted list of tuples containing indices and distances for earlier results, reversed so we have biggest first and remove first elements since its the node itself
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1], reverse=True)[:-1]
            # list to store titles

            rec = []
            i = 0
            for val in rec_movie_indices:
                movie_idx = self.final_dataset.iloc[val[0]]['movieId']
                idx = self.movies[self.movies['movieId'] == movie_idx].index
                # append title and genres
                rec.append((self.movies.iloc[idx]['title'].values[0], self.movies.iloc[idx]['genres'].values[0].split("|")))
                i += 1

            return rec[::-1]
        
        except Exception as e:
            return []
        

    def get_movie_genre(self, movie_name):
        movie_name = re.sub(r'\([^)]*\)', '', movie_name).strip()

        return self.movies[self.movies['title'].str.contains(movie_name)].iloc[0]['genres'].split("|")

    def get_genre_recommendation(self, genre, num_of_recommendations):
        dt = {}
        dt[genre] = self.movies[self.movies['genres'].str.contains(genre)].sample(n=num_of_recommendations, random_state=42)['title'].tolist()
        return dt