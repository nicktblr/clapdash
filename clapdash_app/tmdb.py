import json

import flask
import pandas as pd
import tmdbsimple as tmdb

from . import app, tmdb_key

tmdb.API_KEY = tmdb_key

@app.route('/tmdb/search/')
def search_tmdb():

    query = flask.request.args.get('name')
    
    search = tmdb.Search()
    response = search.movie(query=query)
    
    movies = search.results

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
