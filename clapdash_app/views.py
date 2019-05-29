import json
from datetime import datetime

import pandas as pd
import requests as req
from flask import Flask, Response, render_template, request, session

from . import app, gsheets, r, tmdb


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/import/headers/<data_type>")
def get_headers(data_type):
    ## TODO: is not?? fix this
    if data_type is not 'gsheets':
        ## TODO: Store URL in session
        url = request.args.get('url')
        id = gsheets.extract_id(url)

        
        ## TODO: Need to pull sheet names
        cell_ranges = 'Sheet1!1:1'
        result = gsheets.get_sheets(id, cell_ranges)
        
        values = result['valueRanges'][0]['values'][0]

    ## TODO: Add process to allow data with no headers

    ## TODO: This process won't work with blank cells
    # Get uppercase ASCII characters for each value to assign column key
    # A=65, Z=90
    ASCII_A = 65
    alp_keys = []
    for letter in range(ASCII_A, ASCII_A + len(values)):
        alp_keys.append(chr(letter))
    

    sheet_headers = dict(zip(alp_keys, values))

    return json.dumps(sheet_headers)


@app.route("/import/data/<data_type>")
def get_data(data_type):
    if data_type == 'gsheets':
        url = request.args.get('url')
        cols = json.loads(request.args.get('cols'))     # Convert json array string to list
        id = gsheets.extract_id(url)

        sheet_name = 'Sheet1!'
        cell_ranges = [sheet_name + col + ':' + col for col in cols]

        result = gsheets.get_sheets(id, cell_ranges)

        ## TODO: slice based on headers or no headers
        # Get list of lists from result
        movies_lol = result['valueRanges'][0]['values'][1::]
        dates_lol = result['valueRanges'][1]['values'][1::]
        scores_lol = result['valueRanges'][2]['values'][1::]

        # Rip strings from lists
        movies = [j for i in movies_lol for j in i]
        dates = [j for i in dates_lol for j in i]
        scores = [j for i in scores_lol for j in i]

    key = data_type + '_' + id
    session['movies_key'] = key

    d = { 'Date': dates, 'name': movies, 'Score': scores }
    movie_list = pd.DataFrame(d)

    movie_list['Date'] = movie_list['Date'].astype('datetime64')
    movie_list['Score'] = movie_list['Score'].astype('int64')

    movie_list = movie_list[::-1]

    set_movies(key, movie_list.to_msgpack())

    return Response(str(len(movies)), mimetype='text/html', status=200)


def set_movies(key, movie_list):
    r.set(key, movie_list)

def tmdb_viewmodel(movie_list):
    tmdb_data = pd.DataFrame(movie_list)
    return tmdb_data


@app.route('/movies/', methods=['GET','POST'])
def movies():
    if request.method == 'POST':
        tmdb_data = json.loads(request.form['data'])

        for i in range(len(tmdb_data)):
            tmdb_data[i] = json.loads(tmdb_data[i])
            
        movies = get_movies(-1)
        movies = movies.set_index(['name'], drop=False)
        movies.index.name = None
        tmdb_model = tmdb_viewmodel(tmdb_data)
        tmdb_model = tmdb_model.set_index(['name'], drop=False)
        tmdb_model.index.name = None

        if movies.shape[1] == 3:
            movies = pd.merge(movies, tmdb_model, on='name', how='left')
        else:
           movies.update(tmdb_model, overwrite=False)

        #joined_movies = pd.merge(movies, tmdb_model, on='name', how='left')

        key = session['movies_key']
        set_movies(key, movies.to_msgpack())

        return Response("Data Joined.", mimetype='text/html', status=200)
    
    page = int(request.args.get('page'))
    movies = get_movies(page)
    
    return movies.to_json(orient='records')


@app.route('/movies/render/')
def render_movies():
    page = int(request.args.get('page'))
    movies = get_movies(page)

    movies['month_watched'] = movies['Date'].map(lambda x: x.strftime('%B %Y'))

    list_of_movies = movies.to_dict(orient='records')
    return render_template('_cards.html', movies=list_of_movies)


@app.route('/movies/render-modal')
def render_modal():
    query_name = request.args.get('name')
    movies = get_movies(-1)
    print(movies)

    movie = movies.loc[movies['name'] == query_name]

    print(movie)

    movie = movie.to_dict(orient='records')

    print(movie)
    print(movie[0])

    return render_template('_movie_modal.html', movie=movie[0])


def get_movies(page=-1):
    MAX_RECORDS = 20

    key = session['movies_key']
    movies_msgpack = r.get(key)
    movies = pd.read_msgpack(movies_msgpack)

    if page != -1:
        if len(movies) < page*MAX_RECORDS:
            return movies.iloc[(page-1)*MAX_RECORDS::]
        return movies.iloc[(page-1)*MAX_RECORDS:(page)*MAX_RECORDS]

    return movies
