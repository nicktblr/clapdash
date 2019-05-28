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

    if not search.results:
        return flask.Response('Nothing found with this name', mimetype='text/html', status=404)

    s = movies[0]

    movie = tmdb.Movies(s['id'])

    r = movie.info()

    movie_vm = {}

    movie_vm['name'] = query
    movie_vm['Title'] = r.get("title") 
    movie_vm['Release Date'] = r.get("release_date")
    movie_vm['Runtime'] = r.get("runtime")
    movie_vm['Original Language'] = r.get("original_language")
    movie_vm['Production Country'] = r.get("production_countries")[0]["name"] if r.get("production_countries") != [] else 'None Listed'
    movie_vm['Poster'] = r.get("poster_path")
    movie_vm['TMDB Score'] = r.get("vote_average")

    return json.dumps(movie_vm)
