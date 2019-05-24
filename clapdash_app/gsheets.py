import os
import flask
import requests
import re

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from . import app

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


@app.route('/gsheets/')
def get_sheets(id='1ePZlwiGKNu72ROwmPR66W0QvVUlnv0uEfy7BckS23IM', cell_range=["Sheet1!A:C"]):
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    sheet = service.spreadsheets()

    result = sheet.values().batchGet(spreadsheetId=id,
        ranges=cell_range).execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    return result
    #return flask.jsonify(**result)


@app.route('/gsheets/login/')
def authorize():
    if 'credentials' in flask.session:
        return flask.Response("Authenticated.", mimetype='text/html', status=200)

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    #return flask.redirect(authorization_url)
    return flask.Response(authorization_url, mimetype='text/html', status=401)


@app.route('/gsheets/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return "Close this window."

    #return flask.redirect(flask.url_for('get_sheets'))


@app.route('/gsheets/login/validate')
def validLogin():
    if 'credentials' in flask.session:
        return flask.Response("Authenticated.", mimetype='text/html', status=200)
    return flask.Response("Not Authenticated.", mimetype='text/html', status=401)


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def extract_id(url):
    return re.search('/spreadsheets/d/([a-zA-Z0-9-_]+)', url).group(1)


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)