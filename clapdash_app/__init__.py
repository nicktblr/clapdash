import flask
import os
app = flask.Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']
# TESTING ONLY
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'