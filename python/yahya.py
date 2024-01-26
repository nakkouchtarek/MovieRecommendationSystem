import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class YahyaRecommender:
    def __init__(self, db, filename="cosine_similarity_matrix.npy"):
        self.movies_data = pd.DataFrame(db.tmdb_5000_movies.find({}))
        credits = pd.DataFrame(db.tmdb_5000_credits.find({}))

        self.movies_data = pd.merge(self.movies_data, credits, on='title')

        self.features = ['keywords', 'cast', 'genres', 'crew']

        for feature in self.features:
            self.movies_data[feature] = self.movies_data[feature].fillna('')

        self.movies_data['combined_features'] = self.movies_data.apply(
            lambda row: row['keywords'] + [" "] + row['cast'] + [" "] + row['genres'] + [" "] + row['crew'], axis=1
        )

        #self.cv = CountVectorizer()
        #self.count_matrix = self.cv.fit_transform(self.movies_data["combined_features"])
        #self.cosine_sim = cosine_similarity(self.count_matrix)
        self.load_cosine_similarity_matrix()

    def save_cosine_similarity_matrix(self, filename="cosine_similarity_matrix.npy"):
        np.save(filename, self.cosine_sim)

    def load_cosine_similarity_matrix(self, filename="cosine_similarity_matrix.npy"):
        self.cosine_sim = np.load(filename)

    def get_recommendations(self, movie_title, num_recommendations=10):
        try:
            movie_title = re.sub(r'\([^)]*\)', '', movie_title).strip()

            movie_index = self._get_index_from_title(movie_title)
            similar_movies = list(enumerate(self.cosine_sim[movie_index]))
            sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)

            recommendations = [
                self._get_title_from_index(movie[0]) for movie in sorted_similar_movies[:num_recommendations]
            ]
            return recommendations
        except:
            return []

    def _get_title_from_index(self, index):
        return self.movies_data[self.movies_data.index == index]["title"].values[0]

    def _get_index_from_title(self, title):
        return self.movies_data[self.movies_data.title == title].index.values[0]