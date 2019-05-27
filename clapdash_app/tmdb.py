import flask

import json

import tmdbsimple as tmdb

from . import app, tmdb_key

import pandas as pd

tmdb.API_KEY = tmdb_key

def search_tmdb(query):
    search = tmdb.Search()
    response = search.movie(query=query)
    
    raw_movies = search.results
    movies = search.results
    
    #movies.sort(key=extract_popularity, reverse=True)

    s = movies[0]
    movie = tmdb.Movies(s['id'])

    return movie.info()

def display_results(movie_names):
    ext_data = pd.DataFrame(columns=['name', 'Title', 'Release Date', 'Runtime', 'Original Language', 'Production Country', 'Poster', 'TMDB Score'])
    for name in movie_names:
        n = search_tmdb(name)


def extract_popularity(json):
    try:
        return float(json['popularity'])
    except KeyError:
        return 0