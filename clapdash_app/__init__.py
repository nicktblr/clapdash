import flask
import os
import redis
app = flask.Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']

# TESTING ONLY
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r = redis.from_url(redis_url)

tmdb_key = os.getenv('TMDB_KEY')