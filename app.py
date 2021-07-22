import os
from flask import Flask, session, request, redirect, render_template
import spotipy
import discogs_client
import uuid
import releasesFinder

app = Flask(__name__)

# adapted from exaples/app.py
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
cache_folder = './.spotify_caches/'
scope = "user-top-read"

session['page'] = 0


d = discogs_client.Client('SpotifyApp/0.1', user_token='XxPisqbcNHfHaDBbvVOiRiFcelaTzcmGpLpQOWFU')

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

def current_session_cache_path():
    return cache_folder + session.get('uuid')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['page'] += 1
        redirect('/')
    
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
        print(auth_url)
        return render_template('signin.html', auth_url=auth_url)
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    releases = releasesFinder.get_releases(sp, d, session['page'])
    return render_template('app.html', releases=releases)

if (__name__ == "__main__"):
    app.run(threaded=True, 
    port=5000)