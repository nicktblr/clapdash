import flask

import json

import tmdbsimple as tmdb

from . import app, tmdb_key

import pandas as pd

tmdb.API_KEY = tmdb_key

@app.route('/tmdb/search/')
def search_tmdb():
    ## Could cache name/id pairs to reduce processing time by ~1/2
    ## Could also just store name/data pairs to reduce processing by more
    query = flask.request.args.get('name')
    
    search = tmdb.Search()
    response = search.movie(query=query)
    
    movies = search.results
    
    #movies.sort(key=extract_popularity, reverse=True)

    s = movies[0]

    movie = tmdb.Movies(s['id'])

    r = movie.info()
    
    movie_vm = {'name': query,
        'Title': r["title"],
        'Release Date': r["release_date"],
        'Runtime': r["runtime"],
        'Original Language': r["original_language"],
        'Production Country': r["production_countries"][0]["name"],
        'Poster': r["poster_path"],
        'TMDB Score': r["vote_average"]
    }

    return json.dumps(movie_vm)


def extract_popularity(json):
    try:
        return float(json['popularity'])
    except KeyError:
        return 0