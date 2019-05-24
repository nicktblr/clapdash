from datetime import datetime

from flask import Flask, render_template, request

from . import app

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
    print(data_type)
    if data_type is not 'gsheets':
        url = request.args.get('url')
        cols = json.loads(request.args.get('cols'))     # Convert json array string to list
        id = gsheets.extract_id(url)
        
        sheet_name = 'Sheet1!'
        cell_ranges = [sheet_name + col + ':' + col for col in cols]
        print(cell_ranges)

        result = gsheets.get_sheets(id, cell_ranges)
        print(result)

        ## TODO: slice based on headers or no headers
        movies = result['valueRanges'][0]['values'][1::]
        dates = result['valueRanges'][1]['values'][1::]
        scores = result['valueRanges'][2]['values'][1::]

    d = { 'Date': dates, 'Title': movies, 'Score': scores }
    df = pd.DataFrame(d)

    return df.to_json(orient='records')
