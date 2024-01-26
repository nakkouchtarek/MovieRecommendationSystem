#!/home/user/Stuff/pythonml/env/bin/python

from fastapi.responses import JSONResponse
import spacy
from threading import Thread
import re, json
from model_movie import MovieRecommendationEngine
import pandas as pd
from ast import literal_eval
import jwt
from datetime import datetime, timedelta
import pymongo
from yahya import YahyaRecommender
import random

mongo_uri = "mongodb://localhost:27017/"

client = pymongo.MongoClient(mongo_uri)

db = client.miniflix

movies = pd.DataFrame(db.item_based_movies.find({}))
ratings = pd.DataFrame(db.item_based_ratings.find({}))

# loads spacy's large pretrained language model
nlp = spacy.load("en_core_web_lg")

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import requests

engine = MovieRecommendationEngine(db)
engine2 = YahyaRecommender(db)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_trailer_link(id):
    r = requests.get(f"https://api.themoviedb.org/3/movie/{str(id)}/videos?api_key=2da959128bf01c42309d7a6b378a64df")
    return r.json()

# recursive call to traverse through a dictionary with list values
def remove_null_elements(obj):
    # check if obj is a list
    if isinstance(obj, list):
        # check for each item inside if item is not null
        return [remove_null_elements(item) for item in obj if item is not None]
    elif isinstance(obj, dict):
        # if our object is a dictionary we will go through each value to check its not null by value i mean list
        return {key: remove_null_elements(value) for key, value in obj.items() if value is not None}
    else:
        # if our object is normal we just return the object so it goes back to the base case where we check if its not null
        return obj
    
def remove_dups(obj):
    # Create a set to store unique IDs
    unique_ids = set()

    # List to store dictionaries with unique IDs
    unique_dicts = []

    # Iterate through the list of dictionaries
    for d in obj:
        try:
            # Check if the ID is not in the set of unique IDs
            if d["id"] not in unique_ids:
                # Add the ID to the set
                unique_ids.add(d["id"])
                # Add the dictionary to the list of unique dictionaries
                unique_dicts.append(d)
        except:
            unique_dicts.append(d)

    return unique_dicts

def get_movie_id(movie_name):
    movie_name = ''.join([elem for elem in movie_name.split("The") if elem != '']).strip()
    
    # check if movie exists inside movies df
    movie_exists_mask = movies['title'].str.contains(movie_name, case=False, regex=False)

    # if any result at all
    if movie_exists_mask.any():
        # get first row and return movieId
        first_matching_row = movies.loc[movie_exists_mask].iloc[0]
        return str(first_matching_row['movieId'])

def get_movie_full(name):
    name = re.sub(r'\([^)]*\)', '', name).strip()

    r = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=2da959128bf01c42309d7a6b378a64df&query={name}")
    res = r.json()
    
    # normal lookup per element if name in original name
    for elem in res['results']:
        if name == elem['original_title']:
            return {
                'id': get_movie_id(name),
                'title': elem['original_title'], 
                'poster_path': elem['poster_path'], 
                'overview': elem['overview'],
                'backdrop_path': elem['backdrop_path']
            }
    
    # check if its in the original name
    for elem in res['results']:
        if name in elem['original_title']:
            return {
                'id': get_movie_id(name),
                'title': elem['original_title'], 
                'poster_path': elem['poster_path'], 
                'overview': elem['overview'],
                'backdrop_path': elem['backdrop_path']
            }
        
    return {
            'id': get_movie_id(name),
            'title': res['results'][0]['original_title'], 
            'poster_path': res['results'][0]['poster_path'], 
            'overview': res['results'][0]['overview'],
            'backdrop_path': res['results'][0]['backdrop_path']
        } if len(res['results']) != 0 else {}
        
def get_movie_literal(name):
    name = re.sub(r'\([^)]*\)', '', name).strip()

    r = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=2da959128bf01c42309d7a6b378a64df&query={name}")
    res = r.json()

    if len(res['results']) == 0: return {}

    trap = [',',':','.']

    # if movie has special element it will cause a weird scenario on lookup
    # as it will generate only one movie which is our movie so we return it
    if any(ext in name for ext in trap):
        return {
            'myid': get_movie_id(name), 
            'id': res['results'][0]['id'], 
            'title': res['results'][0]['original_title'], 
            'poster_path': res['results'][0]['poster_path'], 
            'overview': res['results'][0]['overview'],
            'backdrop_path': res['results'][0]['backdrop_path'],
            'genres': res['results'][0]['genre_ids'],
        }

    for elem in res['results']:
        if name == elem['original_title']:
            return {
                'myid': get_movie_id(name), 
                'id': res['results'][0]['id'], 
                'title': elem['original_title'], 
                'poster_path': elem['poster_path'], 
                'overview': elem['overview'],
                'backdrop_path': elem['backdrop_path'],
                'genres': res['results'][0]['genre_ids'],
            }

def recommend_movie(name, engine=engine, engine2=engine2):
    res = engine.get_movie_recommendation_with_genre(name, 20)
    recommendations = engine2.get_recommendations(name)

    # base cases to handle
    if not res and not recommendations: return []
    if not res: return recommendations
    if not recommendations: return random.sample(res, min(10, len(res)))
    
    # for each movie inside recommendations ( engine2 )
    for i, elem in enumerate(recommendations):
        elem = str(elem)
        # check if movie exists inside our movies.csv
        x = movies[movies['title'].str.contains(elem.strip())].head(1)['title']

        if x.empty:
            recommendations.remove(elem)
        else:
            # add movie and genre to list
            recommendations[i] = (elem, movies[movies['title'].str.contains(elem.strip())].head(1)['genres'].values[0])

    # get list of unique movies inside recommendations
    recommendations = list(set(recommendations))
    # get 5 random movies from our recommendations
    recommendations = random.sample(recommendations, min(5, len(recommendations)))

    # now we iterate through res until we reach 10 movies
    for i, item in enumerate(res):
        m, g = item

        # clean movie name
        item = re.sub(r'\([^)]*\)', '', m).strip()

        # if item not in recommendations add it
        if item not in recommendations:
            recommendations.append((item, g))

        # break loop if we reach 10 movies
        if len(recommendations) == 10:
            break
    
    return recommendations

def get_high_rated_movies(userId, sample_size):
    # get movies rated by our user
    user_data = ratings[ratings['userId'] == int(userId)]

    # get the 30 latest rated movies
    user_sorted = user_data.sort_values(by='timestamp', ascending=False).head(30)
    
    # get 3 of those 30 that also have a 4.0 or above rating
    high_rated_movies = user_sorted[user_sorted['rating'] >= 4.0]
    high_rated_movies = high_rated_movies.sample(min(sample_size, len(high_rated_movies)))

    # get the movieIds of those movies and then turn it to list and return it
    return high_rated_movies['movieId'].tolist()

def three_latest_movies_mix(userId):
    try:
        # get 3 of the last highest rated movies by user
        high_rated_movies = get_high_rated_movies(userId, 3)
        
        # our return list
        res = []
        
        # iterate through each movieId inside our high_rated_movies list
        for movieId in high_rated_movies:
            # get name of movie from movieId
            name = movies[movies['movieId'] == movieId].values[0][2]

            # now we will get movie recommendation for each movie
            for elem in recommend_movie(name, engine, engine2):

                # it returns a tuple of movie, genre so we take movie name only thus elem[0]
                res.append(elem[0])
        
        # from all those movies we return random 10 movies
        return random.sample(res, 10)
    except:
        # on error return empty list
        return []

@app.post('/foryou/')
async def for_you(request: Request):
    data = await request.json()
    token = request.headers.get('Authorization').split(" ")[1]
    userId = jwt.decode(token, "secret", algorithms="HS256")['userId']

    # specify mongodb collection
    collection = db.extension

    # cursor to navigate through our collection
    data = collection.find({})

    # check if user has used extension
    chosen = None

    for document in data:
        # if user has already used the extension, we will find his document
        # and set our chosen variable to it for later use
        if document['userId'] == str(userId):
            chosen = document
            break

    # has extension
    if chosen:
        
        # navigating through extension we will get 3 of each, movies that were viewed 5 or more times, same thing for genres
        movies = [key for (key,value) in sorted(document['details']['movies'].items(), key=lambda x:x[1], reverse=True) if value >= 5]
        movies = random.sample(movies, min(3, len(movies)))

        genres = [key for (key,value) in sorted(document['details']['genres'].items(), key=lambda x:x[1], reverse=True) if value >= 5]
        genres = random.sample(genres, min(3, len(genres)))

        res = []

        for i, movie in enumerate(movies):
            recommendations = recommend_movie(movie, engine, engine2)

            res.append([])

            for item in recommendations:
                m, g = item[0], item[1]

                # check if movie has genres user is interested in
                if all(element in g for element in genres):
                    res[i].append(m)

                # get 3 random movies from res[i]
                res[i] = random.sample(res[i], min(3, len(res[i])))
        
        # turn our list of lists into a list
        res = list(set([item for sublist in res for item in sublist]))

        # not enough movies caught from extension
        if len(res) < 8:
            res = res + three_latest_movies_mix(userId)
            res = res[:8]

    # no extension
    else:
        res = three_latest_movies_mix(userId)
    
    results = []
    threads = []

    # launch a thread that will fetch each movie information using tmdb api and then add it to our results list
    for movie in list(set(res))[:8]:
        threads.append(Thread(target=lambda movie=movie: results.append(get_movie_full(movie))))

    # start threads
    for thread in threads:
        thread.start()
    
    # wait for threads to finish
    for thread in threads:
        thread.join()
    
    return remove_dups(remove_null_elements(results))

@app.post('/liked/')
async def because_you_liked(request: Request):
    try:
        data = await request.json()
        token = request.headers.get('Authorization').split(" ")[1]
        userId = jwt.decode(token, "secret", algorithms="HS256")['userId']
        
        # get 3 of the last highest rated movies by user
        last_20_high_rated_movies = get_high_rated_movies(userId, 3)

        # dictionary for results from recommendation
        res = {}

        for movieId in last_20_high_rated_movies:
            # get movie name            
            name = movies[movies['movieId'] == movieId].values[0][2]

            res[name] = []
            
            # get movie recommendations for movie
            for elem in recommend_movie(name, engine, engine2):
                # add movie name to list
                res[name].append(elem[0])

        # another dictionary for final results
        results = {}
        threads = []

        # iterate through each main movie title 
        for elem in res:
            results[elem] = []

            # iterate through each iteration
            for movie in set(res[elem]):
                # start a thread to find movie details using tmdb api and append them to list
                threads.append(Thread(target=lambda movie=movie,elem=elem: results[elem].append(get_movie_full(movie))))

        # start threads
        for thread in threads:
            thread.start()

        # wait for threads
        for thread in threads:
            thread.join()

        # check for each key in results if key is null or whether we got a special case where the movie would return 'E' we delete the key in both cases
        for elem in list(results.keys()):
            if not results[elem] or (len(results[elem]) == 1 and results[elem][0]['title'] == 'E'):
                del results[elem]

        # another clearing of the elements to give out clean data
        results = remove_null_elements(results)

        for elem in results:
            results[elem] = remove_dups(results[elem])

        return results
    except:
        return []

@app.get('/discover/')
def discover_movies_genre(genre: str):
    # get each movies average rating
    average_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()

    # count how many times movie has been rated
    movie_count = ratings['movieId'].value_counts()

    # merge our movie count with our average_ratings dataframe based on movieId column
    average_ratings = pd.merge(average_ratings, movie_count, on='movieId')
    
    # merge our average ratings and movies dataframes based on movieId column
    merged_movies = pd.merge(average_ratings, movies, on='movieId')

    # get movies that have more than 20 votes and a rating of 4.0 or more, also check if the movie is of the requested genre, we will get 10 movies
    high_rated_genre_movies = merged_movies[(merged_movies['count'] > 20) & (merged_movies['rating'] >= 4.0) & merged_movies['genres'].str.contains(genre)]
    high_rated_genre_movies = high_rated_genre_movies.sample(min(10, len(high_rated_genre_movies)))

    results = []
    threads = []

    # we tranform our high_rated_genre_movies dataframe to a list then iterate through each movie in it
    for movie in high_rated_genre_movies['title'].tolist():
        # thread to get movie information using tmdb api
        threads.append(Thread(target=lambda movie=movie: results.append(get_movie_full(movie))))

    # start threads
    for thread in threads:
        thread.start()

    # wait for threads to finish
    for thread in threads:
        thread.join()
    
    # clean dictionnary
    return remove_null_elements(results)

@app.get('/random/')
def discover_movies_genre():
    # get each movies average rating
    average_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()

    # count how many times movie has been rated
    movie_count = ratings['movieId'].value_counts()

    # merge our movie count with our average_ratings dataframe based on movieId column
    average_ratings = pd.merge(average_ratings, movie_count, on='movieId')
    
    # merge our average ratings and movies dataframes based on movieId column
    merged_movies = pd.merge(average_ratings, movies, on='movieId')

    # get movies that have more than 20 votes and a rating of 4.0 or more, also check if the movie is of the requested genre, we will get 10 movies
    high_rated_genre_movies = merged_movies[(merged_movies['count'] > 20) & (merged_movies['rating'] >= 4.0)]

    total = []

    for genre in ['Action','Adventure','Thriller','Romance','Horror']:
        tmp = high_rated_genre_movies[high_rated_genre_movies['genres'].str.contains(genre)]
        tmp = tmp.sample(min(3, len(tmp)))

        for m in tmp['title'].tolist():
            total.append(m)

    results = []
    threads = []

    # we tranform our high_rated_genre_movies dataframe to a list then iterate through each movie in it
    for movie in total:
        # thread to get movie information using tmdb api
        threads.append(Thread(target=lambda movie=movie: results.append(get_movie_full(movie))))

    # start threads
    for thread in threads:
        thread.start()

    # wait for threads to finish
    for thread in threads:
        thread.join()
    
    # clean dictionnary
    return remove_null_elements(results)

def extract_titles(text):
    # process text which tokenizes it and gives labels to each through its nlp model
    doc = nlp(text)
    # we fetch all the entities the model has identified inside our document that we got
    ents = doc.ents
    # we will get only the text of entities whom the model identified as work of art
    return [ent.text for ent in ents if ent.label_ == "WORK_OF_ART"]

def handle_res(results, userId):
    titles = {}
    genres = {}

    collection = db.extension

    data = collection.find({})

    # hold unique titles only
    words = set()

    # iterate through each line of our scraped results
    for elem in results:
        # if our element is not code
        if elem[0] not in ["•",".","#","-","{","/"]:
            # we will extract all the titles from it
            for elem in extract_titles(elem):
                words.add(elem)

    # iterate through each word
    for word in words:

        # a first lookup to see if any title starts with it
        search = movies[movies['title'].str.startswith(word)] 

        # if still empty, see if theres an element that contains the word
        search = movies[movies['title'].str.contains(word)] if search.empty else search

        # if we found the title we're looking for, we operate
        if not search.empty:
            # get first row from dataframe
            search = search.head(1)

            # get the title value
            title = search['title'].values[0]
            
            # set the value inside our dictionary to one
            titles[title] = 1
            
            # for genres, its another case, since we can have multiple movies
            # but same genre, so we actually increment on multiple appearences
            for genre in str(search['genres'].values[0]).split("|"):

                if genre in genres:
                    genres[genre] += 1
                else:
                    genres[genre] = 1

    # sort our dictionaries by value
    titles = dict(sorted(titles.items(), key=lambda x:x[1], reverse=True))
    genres = dict(sorted(genres.items(), key=lambda x:x[1], reverse=True))

    # check if user exists inside extension collection
    chosen = None
    for document in data:
        if document['userId'] == str(userId):
            chosen = document['userId']

    if not chosen:
        new_document = {
            "userId": str(userId),
            "details":{
                "movies":{},
                "genres":{}
            }
        }
        collection.insert_one(new_document)

    for key, value in titles.items():
        update_expression = {
            "$inc": {"details.movies." + key.replace('.', '/'): value},
            "$setOnInsert": {"userId": userId}
        }
        collection.update_one({"userId": userId}, update_expression, upsert=True)

    for key, value in genres.items():
        update_expression = {
            "$inc": {"details.genres." + key.replace('.', '/'): value},
            "$setOnInsert": {"userId": userId}
        }
        collection.update_one({"userId": userId}, update_expression, upsert=True)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/extension/")
async def read_item(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        token = request.headers.get('Authorization').split(" ")[1]
        userId = jwt.decode(token, "secret", algorithms="HS256")['userId']
        background_tasks.add_task(handle_res, data["results"], userId)
        print(userId)
        return {"ok":"ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/login/")
async def login(request: Request):
    try:
        data = await request.json()
        username = data['username']
        password = data['password']

        collection = db.users

        data = collection.find({})

        for document in data: 
            details = document['details']

            if username == details['username'] and password == details['password']:
                
                future_datetime = datetime.now() + timedelta(hours=24)
                future_datetime = future_datetime.strftime("%Y-%m-%d %H:%M:%S")
                encoded_jwt = jwt.encode({"expiration":f"{future_datetime}", "userId":document['userId']}, "secret", algorithm="HS256")

                return {"token":encoded_jwt}
        
        return {"token":""}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/register/")
async def check_validity(request: Request):
    received = await request.json()

    collection = db.users

    data = collection.find({})

    for document in data: 
        details = document['details']
        
        if details['username'] == received['username']:
            return {"state":"User already exits"}

    latest_document = int(collection.find_one(sort=[("_id", pymongo.DESCENDING)])['userId'])+1

    result = collection.insert_one({
        "userId": str(latest_document),
        "details": {
        "username": received['username'],
        "password": received['password'],
        "ddn": received['dnn'],
        "sexe": received['sexe'],
        "pays": received['pays']
    }
    })

    return {"state":"created"}

@app.post("/check_validity/")
async def check_validity(request: Request):
    data = await request.json()

    exp = jwt.decode(data['token'],"secret","HS256")

    if datetime.strptime(exp['expiration'], "%Y-%m-%d %H:%M:%S") > datetime.now():
        return {"state":"valid"}
    else:
        return {"state":"expired"}
    
@app.post("/get_user/")
async def check_validity(request: Request):
    data = await request.json()
    token = request.headers.get('Authorization').split(" ")[1]
    userId = jwt.decode(token,"secret","HS256")['userId']

    collection = db.users

    data = collection.find({})

    for document in data:
            if userId == document['userId']:
                details = document['details']

                return {
                    'username': details['username'],
                    'ddn': details['ddn'],
                    'sexe': details['sexe'],
                    'pays': details['pays']
                }
            
    return {}

@app.post("/update_user/")
async def check_validity(request: Request):
    data = await request.json()
    token = request.headers.get('Authorization').split(" ")[1]
    userId = jwt.decode(token,"secret","HS256")['userId']

    collection = db.users

    if data['password'] == '':
        for document in data:
            if userId == document['userId']:
                details = document['details']
                data['password'] = details['password']
                break


    result = collection.update_one(
    {"userId": userId},
    {"$set": {"details": data}}
    )

    if result.matched_count > 0:
        return {"state":"ok"}
    else:
        return {"state":"failed"}
    
@app.get('/popular_movie/')
def discover_movies_genre():
    # get each movies average rating
    average_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()

    # count how many times movie has been rated
    movie_count = ratings['movieId'].value_counts()

    # merge our movie count with our average_ratings dataframe based on movieId column
    average_ratings = pd.merge(average_ratings, movie_count, on='movieId')
    
    # merge our average ratings and movies dataframes based on movieId column
    merged_movies = pd.merge(average_ratings, movies, on='movieId')

    # extract year from all movies and put it in year column
    merged_movies['year'] = merged_movies['title'].str.extract(r'\((\d{4})\)')

    # Convert the extracted year to numeric type
    merged_movies['year'] = pd.to_numeric(merged_movies['year'], errors='coerce')

    # Filter based on your conditions
    high_rated_genre_movies = merged_movies[(merged_movies['count'] > 20) & 
                                            (merged_movies['rating'] >= 4.0) & 
                                            (merged_movies['year'] > 2005)]

    # Drop the temporary 'year' column if you don't need it anymore
    high_rated_genre_movies = high_rated_genre_movies.drop('year', axis=1)

    # clean dictionnary
    return get_movie_full(high_rated_genre_movies.sample(min(1, len(high_rated_genre_movies)))['title'].values[0])

@app.get('/search_movie/')
def discover_movies_genre(name: str):
    movie_results = movies[movies['title'].str.lower().str.contains(name.lower().strip())].head(33)

    results = []
    threads = []

    # we tranform our high_rated_genre_movies dataframe to a list then iterate through each movie in it
    for movie in movie_results['title'].tolist():
        # thread to get movie information using tmdb api
        threads.append(Thread(target=lambda movie=movie: results.append(get_movie_literal(movie))))

    # start threads
    for thread in threads:
        thread.start()

    # wait for threads to finish
    for thread in threads:
        thread.join()
    
    # clean dictionnary
    return remove_null_elements(results)

@app.get('/movie_details/')
def get_movie(name: str):
    movie = get_movie_literal(name)

    movie["recommendations"] = []

    threads = []

    for key in recommend_movie(name):
        if isinstance(key, tuple):
            key = key[0]
            
        threads.append(Thread(target=lambda m=key: movie["recommendations"].append(get_movie_literal(m))))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    movie["recommendations"] = remove_dups(movie["recommendations"])

    for key in get_trailer_link(movie['id'])['results']:
        if "Trailer" in key['name']:
            movie["trailer"] = f"{key['key']}"
            return movie
        
    return movie

@app.post('/rate_movie/')
async def rate_movie(request: Request):
    data = await request.json()
    token = request.headers.get('Authorization').split(" ")[1]
    userId = jwt.decode(token,"secret","HS256")['userId']

    collection = db.item_based_ratings

    new_document = {
        "userId": int(userId),
        "movieId": int(data["movieId"]),
        "rating": int(data["rating"]),
        "timestamp": int(datetime.now().timestamp()),
    }

    collection.insert_one(new_document)

    return {"ok":"ok"}