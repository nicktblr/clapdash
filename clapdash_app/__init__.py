import flask
import os
app = flask.Flask(__name__)
app.secret_key = 'INSERT SECRET KEY'
# TESTING ONLY
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'