from datetime import datetime

from flask import Flask, render_template, request, session

from . import app, r

from . import gsheets

import requests as req

import json

import pandas as pd


@app.route("/")
def home():
    # movies_obj = gsheets.get_sheets()
    # movies = movies_obj['values']
    
    return render_template("home.html")


@app.route("/headers/<data_type>")
def get_headers(data_type):
    print(data_type)
    ## TODO: is not?? fix this
    if data_type is not 'gsheets':
        ## TODO: Store URL in session
        url = request.args.get('url')
        print(url)
        id = gsheets.extract_id(url)

        
        ## TODO: Need to pull sheet names
        cell_ranges = 'Sheet1!1:1'
        result = gsheets.get_sheets(id, cell_ranges)
        
        print(result)

        values = result['valueRanges'][0]['values'][0]

    ## TODO: Add process to allow data with no headers

    ## TODO: This process won't work with blank cells
    # Get uppercase ASCII characters for each value to assign column key
    # A=65, Z=90
    ASCII_A = 65
    alp_keys = []
    for letter in range(ASCII_A, ASCII_A + len(values)):
        alp_keys.append(chr(letter))
    
    print(alp_keys)
    print(values)

    sheet_headers = dict(zip(alp_keys, values))

    return json.dumps(sheet_headers)


@app.route("/data/<data_type>")
def get_data(data_type):
    if data_type == 'gsheets':
        url = request.args.get('url')
        cols = json.loads(request.args.get('cols'))     # Convert json array string to list
        id = gsheets.extract_id(url)

        sheet_name = 'Sheet1!'
        cell_ranges = [sheet_name + col + ':' + col for col in cols]

        result = gsheets.get_sheets(id, cell_ranges)

        print(result)

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
    print(key)

    d = { 'Date': dates, 'Title': movies, 'Score': scores }
    movie_list = pd.DataFrame(d)
    print(movie_list)

    set_movies(key, movie_list.to_msgpack())

    return movie_list.to_json(orient='records')


def set_movies(key, movie_list):
    r.set(key, movie_list)
    print(r.get(key))

@app.route('/movies/')
def get_movies():
    key = session['movies_key']
    movies_msgpack = r.get(key)
    movies = pd.read_msgpack(movies_msgpack)

    print(movies)

    return movies.to_json(orient='records')
    