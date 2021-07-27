import os
from flask import Flask, session, request, redirect, render_template
from flask_caching import Cache
import spotipy
import discogs_client
import uuid
import releasesFinder
import compress_pickle

DISCOGS_USER_ID = os.getenv('DISCOGS_USER_ID')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


# adapted from exaples/app.py
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
cache_folder = './.spotify_caches/'
scope = "user-top-read"

d = discogs_client.Client('VinylFinder/0.1', 
user_token=DISCOGS_USER_ID)

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

def current_session_cache_path():
    return cache_folder + session.get('uuid')

@app.route('/', methods=['GET', 'POST'])
def index():    
    if not session.get('uuid'):
        # assign user ID
        session['uuid'] = str(uuid.uuid4())

    
    cache_handler = spotipy.CacheFileHandler(cache_path=current_session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    if request.args.get("code"):
        # redirect from spotify
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signin.html', auth_url=auth_url)

    if session.get('releases'):
        return redirect('/vinyls')

    sp = spotipy.Spotify(auth_manager=auth_manager)
    releases = releasesFinder.get_releases(sp, d, 0)
    releases = releases[:min(len(releases), 25)]
    session['releases'] = render_template('app.html', releases=releases, page=0)
    return redirect('/vinyls')
    
    
@app.route('/vinyls', methods=['GET', 'POST'])
@cache.cached(timeout=50)
def callback():
    if not session.get('releases'):
        return redirect('/')
    return compress_pickle.load(session['releases'], 'bz2')
    

if (__name__ == "__main__"):
    app.run(threaded=True)